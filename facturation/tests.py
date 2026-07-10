from datetime import date
from decimal import Decimal

from django.core import mail
from django.test import TestCase, override_settings
from ninja.testing import TestClient

from accounts.models import Role, User
from accounts.test_helpers import auth_headers
from api.v1.router import api
from facturation.models import StatutFacture, TarifActe
from facturation.services import (
    FacturationError,
    enregistrer_paiement,
    generer_facture,
    valider_facture,
)
from hospitalisation.services import admettre_patient
from logistics.models import Batiment, Chambre, Lit, Service
from patients.models import Patient, Sexe
from prescriptions.models import DiagnosticCIM10
from prescriptions.services import ajouter_ligne, creer_prescription, valider_prescription


class FacturationServiceTests(TestCase):
    def setUp(self):
        TarifActe.objects.create(code='ADMISSION', libelle='Admission', categorie='sejour', prix_unitaire=Decimal('10000'))
        TarifActe.objects.create(code='SEJOUR_JOUR', libelle='Jour', categorie='sejour', prix_unitaire=Decimal('5000'))
        TarifActe.objects.create(code='LAB_ANALYSE', libelle='Labo', categorie='laboratoire', prix_unitaire=Decimal('3000'))
        TarifActe.objects.create(code='PHARMA_LIGNE', libelle='Pharma', categorie='pharmacie', prix_unitaire=Decimal('2000'))

        batiment = Batiment.objects.create(code='F', nom='Factu')
        service = Service.objects.create(batiment=batiment, code='MED', nom='Médecine')
        chambre = Chambre.objects.create(service=service, numero='701')
        self.lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient = Patient.objects.create(
            numero_dossier='P-FAC-001',
            nom='Factu',
            prenom='Test',
            date_naissance=date(1987, 7, 7),
            sexe=Sexe.FEMININ,
            consentement_donnees=True,
        )
        self.medecin = User.objects.create_user(username='med_fac', password='x', role=Role.MEDECIN)
        self.comptable = User.objects.create_user(username='comptable_fac', password='x', role=Role.COMPTABLE)
        self.hospitalisation = admettre_patient(
            patient=self.patient,
            lit=self.lit,
            motif_admission='Soins',
            lit_version=self.lit.version,
        )
        DiagnosticCIM10.objects.create(code='J06.9', libelle='IVRS')
        prescription = creer_prescription(
            hospitalisation=self.hospitalisation,
            medecin=self.medecin,
            codes_cim10=['J06.9'],
        )
        ajouter_ligne(prescription=prescription, medicament='Test', posologie='1/j')
        valider_prescription(prescription=prescription, medecin=self.medecin, version=prescription.version)

    def test_generer_et_valider_facture(self):
        facture = generer_facture(hospitalisation=self.hospitalisation, comptable=self.comptable)
        self.assertEqual(facture.statut, StatutFacture.BROUILLON)
        self.assertGreater(facture.montant_total, Decimal('0'))
        self.assertTrue(facture.lignes.filter(code_acte='ADMISSION').exists())

        facture = valider_facture(
            facture=facture,
            comptable=self.comptable,
            version=facture.version,
        )
        self.assertEqual(facture.statut, StatutFacture.VALIDEE)
        self.assertTrue(facture.numero_facture.startswith('FACT-'))
        self.assertTrue(facture.est_verrouillee)

        with self.assertRaises(FacturationError) as ctx:
            generer_facture(hospitalisation=self.hospitalisation, comptable=self.comptable)
        self.assertEqual(ctx.exception.code, 'facture_verrouillee')

    def test_paiement_apres_validation(self):
        facture = generer_facture(hospitalisation=self.hospitalisation, comptable=self.comptable)
        facture = valider_facture(
            facture=facture,
            comptable=self.comptable,
            version=facture.version,
        )
        facture = enregistrer_paiement(
            facture=facture,
            comptable=self.comptable,
            version=facture.version,
            mode_paiement='especes',
            reference_paiement='REC-001',
        )
        self.assertEqual(facture.statut, StatutFacture.PAYEE)


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    EMAIL_NOTIFICATIONS_ENABLED=True,
)
class FacturationEmailTests(TestCase):
    def setUp(self):
        TarifActe.objects.create(code='ADMISSION', libelle='Admission', categorie='sejour', prix_unitaire=Decimal('10000'))
        TarifActe.objects.create(code='SEJOUR_JOUR', libelle='Jour', categorie='sejour', prix_unitaire=Decimal('5000'))

        batiment = Batiment.objects.create(code='FE', nom='Factu Email')
        service = Service.objects.create(batiment=batiment, code='MED', nom='Médecine')
        chambre = Chambre.objects.create(service=service, numero='801')
        lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient = Patient.objects.create(
            numero_dossier='P-FAC-MAIL',
            nom='Mail',
            prenom='Factu',
            date_naissance=date(1990, 2, 2),
            sexe=Sexe.FEMININ,
            email='factu.patient@test.local',
            consentement_donnees=True,
        )
        self.comptable = User.objects.create_user(username='comptable_mail', password='x', role=Role.COMPTABLE)
        self.hospitalisation = admettre_patient(
            patient=self.patient,
            lit=lit,
            motif_admission='Test mail',
            lit_version=lit.version,
        )

    def test_emails_validation_et_paiement(self):
        facture = generer_facture(hospitalisation=self.hospitalisation, comptable=self.comptable)
        with self.captureOnCommitCallbacks(execute=True):
            facture = valider_facture(
                facture=facture,
                comptable=self.comptable,
                version=facture.version,
            )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('facture', mail.outbox[0].subject.lower())

        mail.outbox.clear()
        with self.captureOnCommitCallbacks(execute=True):
            enregistrer_paiement(
                facture=facture,
                comptable=self.comptable,
                version=facture.version,
                mode_paiement='especes',
                montant=Decimal('5000'),
            )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('paiement', mail.outbox[0].subject.lower())


class FacturationAPITests(TestCase):
    def setUp(self):
        TarifActe.objects.create(code='ADMISSION', libelle='Admission', categorie='sejour', prix_unitaire=Decimal('10000'))
        TarifActe.objects.create(code='SEJOUR_JOUR', libelle='Jour', categorie='sejour', prix_unitaire=Decimal('5000'))

        self.client = TestClient(api)
        self.comptable = User.objects.create_user(
            username='comptable_api',
            password='Comptable@SGHL2026',
            role=Role.COMPTABLE,
            mfa_enabled=True,
        )
        self.headers = auth_headers(self.comptable)

        batiment = Batiment.objects.create(code='FA', nom='Bloc')
        service = Service.objects.create(batiment=batiment, code='MED', nom='Médecine')
        chambre = Chambre.objects.create(service=service, numero='801')
        self.lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient = Patient.objects.create(
            numero_dossier='P-FAC-API',
            nom='API',
            prenom='Factu',
            date_naissance=date(1995, 1, 1),
            sexe=Sexe.MASCULIN,
            consentement_donnees=True,
        )
        self.hospitalisation = admettre_patient(
            patient=self.patient,
            lit=self.lit,
            motif_admission='Bilan',
            lit_version=self.lit.version,
        )

    def test_workflow_facturation_api(self):
        gen = self.client.post(
            f'/hospitalisations/{self.hospitalisation.id}/facture/generer/',
            headers=self.headers,
        )
        self.assertEqual(gen.status_code, 200)
        facture_id = gen.json()['id']
        version = gen.json()['version']

        val = self.client.post(
            f'/facturation/factures/{facture_id}/valider/',
            json={'version': version},
            headers=self.headers,
        )
        self.assertEqual(val.status_code, 200)
        self.assertEqual(val.json()['statut'], 'validee')
        version = val.json()['version']

        pay = self.client.post(
            f'/facturation/factures/{facture_id}/paiement/',
            json={'version': version, 'mode_paiement': 'mobile_money', 'reference_paiement': 'MM-123'},
            headers=self.headers,
        )
        self.assertEqual(pay.status_code, 200)
        self.assertEqual(pay.json()['statut'], 'payee')

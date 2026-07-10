from datetime import date
from decimal import Decimal

from django.test import TestCase
from ninja.testing import TestClient

from accounts.jwt_service import create_access_token
from accounts.models import Role, User
from api.v1.router import api
from facturation.models import StatutFacture, TarifActe
from facturation.services import generer_facture, valider_facture
from hospitalisation.services import admettre_patient
from logistics.models import Batiment, Chambre, Lit, Service
from patients.models import Patient, Sexe
from payments.models import Payment


class PatientFacturePaymentTests(TestCase):
    def setUp(self):
        TarifActe.objects.create(
            code='ADMISSION',
            libelle='Admission',
            categorie='sejour',
            prix_unitaire=Decimal('10000'),
        )
        TarifActe.objects.create(
            code='SEJOUR_JOUR',
            libelle='Jour',
            categorie='sejour',
            prix_unitaire=Decimal('5000'),
        )
        batiment = Batiment.objects.create(code='P', nom='Pay')
        service = Service.objects.create(batiment=batiment, code='MED', nom='Médecine')
        chambre = Chambre.objects.create(service=service, numero='901')
        lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient_user = User.objects.create_user(
            username='patient_pay',
            password='x',
            role=Role.PATIENT,
            email='patient_pay@test.local',
        )
        self.patient = Patient.objects.create(
            numero_dossier='P-PAY-001',
            nom='Payeur',
            prenom='Test',
            date_naissance=date(1992, 3, 3),
            sexe=Sexe.MASCULIN,
            compte_utilisateur=self.patient_user,
            consentement_donnees=True,
        )
        self.comptable = User.objects.create_user(username='comptable_pay', password='x', role=Role.COMPTABLE)
        self.hospitalisation = admettre_patient(
            patient=self.patient,
            lit=lit,
            motif_admission='Paiement en ligne',
            lit_version=lit.version,
        )
        facture = generer_facture(hospitalisation=self.hospitalisation, comptable=self.comptable)
        self.facture = valider_facture(
            facture=facture,
            comptable=self.comptable,
            version=facture.version,
        )
        self.client = TestClient(api)
        self.headers = {'Authorization': f'Bearer {create_access_token(self.patient_user)}'}

    def test_list_factures_includes_montant_restant(self):
        res = self.client.get('/patient/factures/', headers=self.headers)
        self.assertEqual(res.status_code, 200, res.content)
        items = res.json()['items']
        self.assertEqual(len(items), 1)
        row = items[0]
        self.assertTrue(row['payable_en_ligne'])
        self.assertGreater(Decimal(str(row['montant_restant'])), Decimal('0'))

    def test_initier_paiement_stripe_simule_solde_facture(self):
        res = self.client.post(
            f'/patient/factures/{self.facture.id}/initier-paiement/',
            json={'provider': 'stripe', 'version': self.facture.version},
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 200, res.content)
        body = res.json()
        self.assertEqual(body['status'], 'success')
        self.assertTrue(body['facture_settled'])

        self.facture.refresh_from_db()
        self.assertEqual(self.facture.statut, StatutFacture.PAYEE)
        self.assertEqual(Payment.objects.filter(reference=body['reference']).count(), 1)

    def test_initier_paiement_refuse_si_deja_payee(self):
        self.client.post(
            f'/patient/factures/{self.facture.id}/initier-paiement/',
            json={'provider': 'stripe', 'version': self.facture.version},
            headers=self.headers,
        )
        self.facture.refresh_from_db()
        res = self.client.post(
            f'/patient/factures/{self.facture.id}/initier-paiement/',
            json={'provider': 'stripe', 'version': self.facture.version},
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 400, res.content)

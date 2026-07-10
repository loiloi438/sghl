from datetime import date

from django.test import TestCase
from ninja.testing import TestClient

from accounts.models import Role, User
from accounts.test_helpers import auth_headers
from api.v1.router import api
from hospitalisation.services import admettre_patient
from logistics.models import Batiment, Chambre, Lit, Service
from patients.models import Patient, Sexe
from prescriptions.models import DiagnosticCIM10, Prescription, StatutPrescription
from prescriptions.services import (
    PrescriptionError,
    ajouter_ligne,
    creer_prescription,
    valider_prescription,
)


class PrescriptionServiceTests(TestCase):
    def setUp(self):
        batiment = Batiment.objects.create(code='A', nom='Principal')
        service = Service.objects.create(batiment=batiment, code='MED', nom='Médecine')
        chambre = Chambre.objects.create(service=service, numero='101')
        self.lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient = Patient.objects.create(
            numero_dossier='P-RX-001',
            nom='Rx',
            prenom='Test',
            date_naissance=date(1980, 1, 1),
            sexe=Sexe.MASCULIN,
            consentement_donnees=True,
        )
        self.medecin = User.objects.create_user(
            username='medecin_rx',
            password='Medecin@SGHL2026',
            role=Role.MEDECIN,
        )
        self.hospitalisation = admettre_patient(
            patient=self.patient,
            lit=self.lit,
            motif_admission='Infection',
            lit_version=self.lit.version,
        )
        DiagnosticCIM10.objects.create(code='J06.9', libelle='IVRS')

    def test_validation_verrouille_prescription(self):
        prescription = creer_prescription(
            hospitalisation=self.hospitalisation,
            medecin=self.medecin,
            codes_cim10=['J06.9'],
        )
        ajouter_ligne(
            prescription=prescription,
            medicament='Amoxicilline',
            posologie='500mg x3/j',
        )
        valider_prescription(
            prescription=prescription,
            medecin=self.medecin,
            version=prescription.version,
        )
        prescription.refresh_from_db()
        self.assertEqual(prescription.statut, StatutPrescription.VALIDEE)
        self.assertTrue(prescription.est_verrouillee)

        with self.assertRaises(PrescriptionError) as ctx:
            ajouter_ligne(
                prescription=prescription,
                medicament='Paracétamol',
                posologie='1g',
            )
        self.assertEqual(ctx.exception.code, 'prescription_verrouillee')

    def test_validation_refusee_sans_medicament(self):
        prescription = creer_prescription(
            hospitalisation=self.hospitalisation,
            medecin=self.medecin,
            codes_cim10=['J06.9'],
        )
        with self.assertRaises(PrescriptionError) as ctx:
            valider_prescription(
                prescription=prescription,
                medecin=self.medecin,
                version=prescription.version,
            )
        self.assertEqual(ctx.exception.code, 'prescription_vide')


class PrescriptionAPITests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.medecin = User.objects.create_user(
            username='medecin_api_rx',
            password='Medecin@SGHL2026',
            role=Role.MEDECIN,
            mfa_enabled=True,
        )
        self.headers = auth_headers(self.medecin)

        batiment = Batiment.objects.create(code='B', nom='Annexe')
        service = Service.objects.create(batiment=batiment, code='MED', nom='Médecine')
        chambre = Chambre.objects.create(service=service, numero='201')
        self.lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient = Patient.objects.create(
            numero_dossier='P-RX-API',
            nom='API',
            prenom='Rx',
            date_naissance=date(1991, 4, 4),
            sexe=Sexe.FEMININ,
            consentement_donnees=True,
        )
        self.hospitalisation = admettre_patient(
            patient=self.patient,
            lit=self.lit,
            motif_admission='Fièvre',
            lit_version=self.lit.version,
        )
        DiagnosticCIM10.objects.create(code='R50.9', libelle='Fièvre')

    def test_workflow_prescription_api(self):
        create_resp = self.client.post(
            f'/hospitalisations/{self.hospitalisation.id}/prescriptions/',
            json={'observations': 'Repos', 'codes_cim10': ['R50.9']},
            headers=self.headers,
        )
        self.assertEqual(create_resp.status_code, 200)
        prescription_id = create_resp.json()['id']

        ligne_resp = self.client.post(
            f'/prescriptions/{prescription_id}/lignes/',
            json={'medicament': 'Paracétamol', 'posologie': '1g x3/j', 'duree_traitement': '5 jours'},
            headers=self.headers,
        )
        self.assertEqual(ligne_resp.status_code, 200)

        version = create_resp.json()['version']
        validate_resp = self.client.post(
            f'/prescriptions/{prescription_id}/valider/',
            json={'version': version},
            headers=self.headers,
        )
        self.assertEqual(validate_resp.status_code, 200)
        self.assertEqual(validate_resp.json()['statut'], 'validee')
        self.assertTrue(validate_resp.json()['est_verrouillee'])

        patch_resp = self.client.patch(
            f'/prescriptions/{prescription_id}/',
            json={'observations': 'Modifié', 'version': validate_resp.json()['version']},
            headers=self.headers,
        )
        self.assertEqual(patch_resp.status_code, 403)

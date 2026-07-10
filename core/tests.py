from django.test import TestCase
from ninja.testing import TestClient

from accounts.models import Role, User
from accounts.test_helpers import auth_headers
from api.v1.router import api
from hospitalisation.models import Hospitalisation, StatutHospitalisation
from hospitalisation.services import admettre_patient
from logistics.models import Batiment, Chambre, Lit, Service
from patients.models import Patient, Sexe
from prescriptions.services import creer_prescription


class HealthEndpointTests(TestCase):
    def setUp(self):
        self.client = TestClient(api)

    def test_health_returns_ok(self):
        response = self.client.get('/sante/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['version'], 'v1')


class DashboardStatsTests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.medecin = User.objects.create_user(
            username='med_dashboard',
            password='x',
            role=Role.MEDECIN,
            mfa_enabled=True,
        )
        self.medecin.set_password('Medecin@SGHL2026')
        self.medecin.save()
        self.headers = auth_headers(self.medecin)

        batiment = Batiment.objects.create(code='D', nom='Demo')
        service = Service.objects.create(batiment=batiment, code='S', nom='Svc')
        chambre = Chambre.objects.create(service=service, numero='1')
        lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient = Patient.objects.create(
            numero_dossier='P-DASH',
            nom='Test',
            prenom='Patient',
            date_naissance='1990-01-01',
            sexe=Sexe.MASCULIN,
        )
        admettre_patient(
            patient=self.patient,
            lit=lit,
            motif_admission='Test',
            lit_version=lit.version,
        )
        hosp = Hospitalisation.objects.get(patient=self.patient, statut=StatutHospitalisation.ACTIVE)
        creer_prescription(
            hospitalisation=hosp,
            medecin=self.medecin,
            observations='Brouillon test',
            codes_cim10=[],
        )

    def test_dashboard_stats(self):
        response = self.client.get('/dashboard/stats/', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(data['patients_actifs'], 1)
        self.assertGreaterEqual(data['prescriptions_en_attente'], 1)
        self.assertIn('rdv_aujourdhui', data)
        self.assertIn('rdv_planifies', data)

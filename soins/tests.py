from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone
from ninja.testing import TestClient

from accounts.models import Role, User
from accounts.test_helpers import auth_headers
from api.v1.router import api
from hospitalisation.models import StatutHospitalisation
from hospitalisation.services import admettre_patient, sortir_patient
from logistics.models import Batiment, Chambre, Lit, Service
from patients.models import Patient, Sexe
from soins.models import DosePlanifiee, PlanSoins, StatutDose
from soins.services import SoinsError, doses_omises, get_hospitalisation_active


class SoinsServiceTests(TestCase):
    def setUp(self):
        batiment = Batiment.objects.create(code='A', nom='Principal')
        service = Service.objects.create(batiment=batiment, code='MED', nom='Médecine')
        chambre = Chambre.objects.create(service=service, numero='101')
        self.lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient = Patient.objects.create(
            numero_dossier='P-SOINS-001',
            nom='Soins',
            prenom='Test',
            date_naissance=date(1988, 3, 3),
            sexe=Sexe.MASCULIN,
            consentement_donnees=True,
        )
        self.infirmier = User.objects.create_user(
            username='infirmier_soins',
            password='Infirmier@SGHL2026',
            role=Role.INFIRMIER,
        )
        self.hospitalisation = admettre_patient(
            patient=self.patient,
            lit=self.lit,
            motif_admission='Surveillance',
            lit_version=self.lit.version,
        )

    def test_constantes_refusees_si_hospitalisation_terminee(self):
        sortir_patient(
            hospitalisation=self.hospitalisation,
            hospitalisation_version=self.hospitalisation.version,
        )
        with self.assertRaises(SoinsError) as ctx:
            get_hospitalisation_active(self.hospitalisation.id)
        self.assertEqual(ctx.exception.code, 'hospitalisation_inactive')

    def test_doses_omises_detectees(self):
        plan = PlanSoins.objects.create(
            hospitalisation=self.hospitalisation,
            titre='Antibiothérapie',
            description='Amoxicilline 8h/20h',
            cree_par=self.infirmier,
        )
        DosePlanifiee.objects.create(
            plan_soins=plan,
            medicament='Amoxicilline',
            posologie='500mg',
            heure_prevue=timezone.now() - timedelta(hours=2),
        )
        self.assertEqual(doses_omises(self.hospitalisation.id).count(), 1)


class SoinsAPITests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.user = User.objects.create_user(
            username='infirmier_api',
            password='Infirmier@SGHL2026',
            role=Role.INFIRMIER,
            mfa_enabled=True,
        )
        self.headers = auth_headers(self.user)

        batiment = Batiment.objects.create(code='C', nom='Test')
        service = Service.objects.create(batiment=batiment, code='MED', nom='Médecine')
        chambre = Chambre.objects.create(service=service, numero='301')
        self.lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient = Patient.objects.create(
            numero_dossier='P-SOINS-API',
            nom='API',
            prenom='Soins',
            date_naissance=date(1992, 7, 7),
            sexe=Sexe.FEMININ,
            consentement_donnees=True,
        )
        from hospitalisation.services import admettre_patient

        self.hospitalisation = admettre_patient(
            patient=self.patient,
            lit=self.lit,
            motif_admission='Post-op',
            lit_version=self.lit.version,
        )

    def test_saisie_constantes_vitales(self):
        response = self.client.post(
            f'/hospitalisations/{self.hospitalisation.id}/constantes-vitales/',
            json={
                'temperature': 37.2,
                'tension_systolique': 120,
                'tension_diastolique': 80,
                'frequence_cardiaque': 72,
                'saturation_o2': 98,
            },
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['temperature'], 37.2)

    def test_plan_soins_et_dose(self):
        plan_resp = self.client.post(
            f'/hospitalisations/{self.hospitalisation.id}/plans-soins/',
            json={
                'titre': 'Antalgiques',
                'description': 'Paracétamol toutes les 6h',
            },
            headers=self.headers,
        )
        self.assertEqual(plan_resp.status_code, 200)
        plan_id = plan_resp.json()['id']

        dose_resp = self.client.post(
            f'/plans-soins/{plan_id}/doses/',
            json={
                'medicament': 'Paracétamol',
                'posologie': '1g',
                'heure_prevue': (timezone.now() - timedelta(hours=1)).isoformat(),
            },
            headers=self.headers,
        )
        self.assertEqual(dose_resp.status_code, 200)

        alertes = self.client.get('/soins/alertes/doses-omises/', headers=self.headers)
        self.assertEqual(alertes.status_code, 200)
        self.assertGreaterEqual(len(alertes.json()['items']), 1)

        dose_id = dose_resp.json()['id']
        dose_version = dose_resp.json()['version']
        admin = self.client.post(
            f'/doses/{dose_id}/administrer/',
            json={'version': dose_version},
            headers=self.headers,
        )
        self.assertEqual(admin.status_code, 200)
        self.assertEqual(admin.json()['statut'], StatutDose.ADMINISTREE)

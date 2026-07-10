from datetime import date

from django.test import TestCase
from ninja.testing import TestClient

from accounts.models import Role, User
from accounts.jwt_service import create_access_token
from api.v1.router import api
from patients.models import Patient, Sexe


class PatientsApiTests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.medecin = User.objects.create_user(
            username='med_pat_test',
            password='Medecin@SGHL2026',
            role=Role.MEDECIN,
            mfa_enabled=True,
        )
        self.headers = {'Authorization': f'Bearer {create_access_token(self.medecin)}'}

    def test_create_patient(self):
        res = self.client.post(
            '/patients/',
            json={
                'numero_dossier': 'P-TEST-001',
                'nom': 'TEST',
                'prenom': 'Patient',
                'date_naissance': '1990-01-01',
                'sexe': 'M',
                'consentement_donnees': True,
            },
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 200, res.content)
        self.assertTrue(Patient.objects.filter(nom='TEST').exists())


class ComplementModulesApiTests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.admin = User.objects.create_user(
            username='admin_comp',
            password='Admin@SGHL2026',
            role=Role.ADMIN,
            mfa_enabled=True,
        )
        self.comptable = User.objects.create_user(
            username='compta_comp',
            password='Comptable@SGHL2026',
            role=Role.COMPTABLE,
            mfa_enabled=True,
        )
        self.medecin = User.objects.create_user(
            username='med_comp',
            password='Medecin@SGHL2026',
            role=Role.MEDECIN,
            mfa_enabled=True,
        )
        self.admin_headers = {'Authorization': f'Bearer {create_access_token(self.admin)}'}
        self.compta_headers = {'Authorization': f'Bearer {create_access_token(self.comptable)}'}
        self.med_headers = {'Authorization': f'Bearer {create_access_token(self.medecin)}'}

    def test_parametres_crud(self):
        res = self.client.get('/parametres/', headers=self.admin_headers)
        self.assertEqual(res.status_code, 200)
        version = res.json()['version']
        patch = self.client.patch(
            '/parametres/',
            json={'version': version, 'organization_name': 'SGHL Test'},
            headers=self.admin_headers,
        )
        self.assertEqual(patch.status_code, 200)
        self.assertEqual(patch.json()['organization_name'], 'SGHL Test')

    def test_assurance_organisme(self):
        res = self.client.post(
            '/assurance/organismes/',
            json={'code': 'TEST', 'nom': 'Assurance Test', 'taux_couverture': 75},
            headers=self.compta_headers,
        )
        self.assertEqual(res.status_code, 200, res.content)

    def test_inventaire_article(self):
        res = self.client.post(
            '/inventaire/articles/',
            json={'code': 'ART-001', 'nom': 'Masques FFP2', 'quantite': 100},
            headers=self.admin_headers,
        )
        self.assertEqual(res.status_code, 200, res.content)

    def test_urgences_passage(self):
        res = self.client.post(
            '/urgences/passages/',
            json={'nom_libre': 'Arrivant Test', 'motif': 'Fièvre', 'niveau_triage': 'orange'},
            headers=self.med_headers,
        )
        self.assertEqual(res.status_code, 200, res.content)

    def test_sante_enrichi(self):
        res = self.client.get('/sante/')
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertIn('checks', body)
        self.assertIn('build', body)

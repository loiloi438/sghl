from django.test import TestCase
from ninja.testing import TestClient

from accounts.models import Role, User
from accounts.test_helpers import auth_headers
from api.v1.router import api
from logistics.models import Batiment, Service


class ServicesAPITests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.admin = User.objects.create_user(
            username='admin_services',
            password='Admin@SGHL2026',
            role=Role.ADMIN,
            mfa_enabled=True,
        )
        self.headers = auth_headers(self.admin)

        self.batiment = Batiment.objects.create(code='A', nom='Accueil')
        Service.objects.create(batiment=self.batiment, code='MED', nom='Médecine interne')

    def test_lister_services_et_batiments(self):
        services = self.client.get('/services/', headers=self.headers)
        self.assertEqual(services.status_code, 200)
        self.assertEqual(len(services.json()), 1)
        self.assertEqual(services.json()[0]['batiment_code'], 'A')

        batiments = self.client.get('/services/batiments/', headers=self.headers)
        self.assertEqual(batiments.status_code, 200)
        self.assertEqual(len(batiments.json()), 1)


class PersonnelAPITests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.admin = User.objects.create_user(
            username='admin_personnel',
            password='Admin@SGHL2026',
            role=Role.ADMIN,
            mfa_enabled=True,
        )
        self.medecin = User.objects.create_user(
            username='dr_house',
            password='x',
            role=Role.MEDECIN,
            first_name='Gregory',
            last_name='House',
            email='house@example.com',
            mfa_enabled=True,
        )
        self.infirmier = User.objects.create_user(
            username='nurse_one',
            password='x',
            role=Role.INFIRMIER,
            first_name='Lisa',
            last_name='Cuddy',
            email='cuddy@example.com',
        )
        self.headers = auth_headers(self.admin)

    def test_lister_medecins(self):
        response = self.client.get('/personnel/medecins/', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        items = response.json()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['username'], 'dr_house')
        self.assertTrue(items[0]['mfa_enabled'])

    def test_lister_infirmiers_avec_recherche(self):
        response = self.client.get('/personnel/infirmiers/?search=Lisa', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        items = response.json()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['email'], 'cuddy@example.com')
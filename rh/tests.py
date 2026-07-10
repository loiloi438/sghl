from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone
from ninja.testing import TestClient

from accounts.models import Role, User
from accounts.jwt_service import create_access_token
from api.v1.router import api
from rh.models import Formation, Garde, StatutFormation
from rh.services import RhError, creer_formation, creer_garde, inscrire_personnel


class RhServiceTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_rh',
            password='Admin@SGHL2026',
            role=Role.ADMIN,
        )
        self.medecin = User.objects.create_user(
            username='medecin_rh',
            password='Medecin@SGHL2026',
            role=Role.MEDECIN,
            first_name='Jean',
            last_name='Okemba',
        )

    def test_creer_formation_et_inscription(self):
        today = date.today()
        formation = creer_formation(
            titre='Hygiène',
            formateur='Formateur',
            date_debut=today,
            date_fin=today + timedelta(days=2),
        )
        inscription = inscrire_personnel(formation=formation, personnel=self.medecin)
        self.assertEqual(formation.participants_count, 1)
        self.assertIsNotNone(inscription.id)

    def test_creneau_garde_conflict(self):
        now = timezone.now()
        creer_garde(
            personnel=self.medecin,
            type_garde='jour',
            date_debut=now,
            date_fin=now + timedelta(hours=8),
        )
        with self.assertRaises(RhError) as ctx:
            creer_garde(
                personnel=self.medecin,
                type_garde='nuit',
                date_debut=now + timedelta(hours=2),
                date_fin=now + timedelta(hours=10),
            )
        self.assertEqual(ctx.exception.code, 'creneau_indisponible')


class RhApiTests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.admin = User.objects.create_user(
            username='admin_rh_api',
            password='Admin@SGHL2026',
            role=Role.ADMIN,
            mfa_enabled=True,
        )
        self.medecin = User.objects.create_user(
            username='medecin_rh_api',
            password='Medecin@SGHL2026',
            role=Role.MEDECIN,
            mfa_enabled=True,
        )
        self.headers = {'Authorization': f'Bearer {create_access_token(self.admin)}'}

    def test_stats_rh(self):
        res = self.client.get('/rh/stats/', headers=self.headers)
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertIn('formations_actives', body)

    def test_crud_formation(self):
        today = date.today().isoformat()
        fin = (date.today() + timedelta(days=3)).isoformat()
        create = self.client.post(
            '/rh/formations/',
            json={
                'titre': 'RCP',
                'formateur': 'Dr Test',
                'date_debut': today,
                'date_fin': fin,
                'capacite_max': 15,
            },
            headers=self.headers,
        )
        self.assertEqual(create.status_code, 200, create.content)
        formation_id = create.json()['id']
        listing = self.client.get('/rh/formations/', headers=self.headers)
        self.assertEqual(listing.status_code, 200)
        self.assertTrue(any(f['id'] == formation_id for f in listing.json()))

    def test_acces_refuse_medecin(self):
        headers = {'Authorization': f'Bearer {create_access_token(self.medecin)}'}
        res = self.client.get('/rh/stats/', headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_planning_gardes(self):
        now = timezone.now().isoformat()
        fin = (timezone.now() + timedelta(hours=12)).isoformat()
        res = self.client.post(
            '/rh/gardes/',
            json={
                'personnel_id': self.medecin.id,
                'type_garde': 'jour',
                'date_debut': now,
                'date_fin': fin,
            },
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 200, res.content)
        semaine = self.client.get('/rh/gardes/semaine/', headers=self.headers)
        self.assertEqual(semaine.status_code, 200)
        self.assertEqual(len(semaine.json()), 7)

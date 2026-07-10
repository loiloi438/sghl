from django.test import TestCase, override_settings
from ninja.testing import TestClient

from accounts.models import Role, User
from accounts.test_helpers import auth_headers
from api.v1.router import api
from notifications.push_service import (
    compter_non_lues,
    enregistrer_appareil,
    marquer_lu,
    notifier_utilisateur,
)
from patients.models import Patient, Sexe
from datetime import date


@override_settings(PUSH_NOTIFICATIONS_ENABLED=True, FCM_SERVER_KEY='')
class PushServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='patient_push',
            password='x',
            role=Role.PATIENT,
            email='push@test.local',
        )
        self.patient = Patient.objects.create(
            numero_dossier='P-PUSH',
            nom='Push',
            prenom='Test',
            date_naissance=date(1995, 1, 1),
            sexe=Sexe.MASCULIN,
            compte_utilisateur=self.user,
            consentement_donnees=True,
        )
        enregistrer_appareil(
            utilisateur_id=self.user.id,
            token='sghl-dev:abc123',
            plateforme='android',
        )

    def test_inbox_et_compteur(self):
        notif = notifier_utilisateur(
            utilisateur_id=self.user.id,
            titre='RDV confirmé',
            corps='Demain à 10h',
            categorie='rendez_vous',
        )
        self.assertEqual(compter_non_lues(self.user.id), 1)
        self.assertTrue(marquer_lu(notif.id, self.user.id))
        self.assertEqual(compter_non_lues(self.user.id), 0)


@override_settings(PUSH_NOTIFICATIONS_ENABLED=True, FCM_SERVER_KEY='')
class NotificationAPITests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.user = User.objects.create_user(
            username='admin_notifications',
            password='Admin@SGHL2026',
            role=Role.ADMIN,
            email='admin-notif@test.local',
            mfa_enabled=True,
        )
        self.headers = auth_headers(self.admin)

    def test_liste_et_marquer_lue(self):
        notif = notifier_utilisateur(
            utilisateur_id=self.user.id,
            titre='Nouvelle alerte',
            corps='Une mise à jour système est disponible.',
            categorie='systeme',
        )

        response = self.client.get('/notifications/', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.json().get('items', [])), 1)

        count = self.client.get('/notifications/non-lues/', headers=self.headers)
        self.assertEqual(count.status_code, 200)
        self.assertEqual(count.json()['count'], 1)

        mark = self.client.post(f'/notifications/{notif.id}/lu/', headers=self.headers)
        self.assertEqual(mark.status_code, 200)

        count_after = self.client.get('/notifications/non-lues/', headers=self.headers)
        self.assertEqual(count_after.status_code, 200)
        self.assertEqual(count_after.json()['count'], 0)

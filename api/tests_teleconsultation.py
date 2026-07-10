from datetime import timedelta

from django.test import TestCase, override_settings
from django.utils import timezone
from ninja.testing import TestClient

from accounts.models import Role, User
from api.v1.router import api
from patients.models import Patient, Sexe
from rendezvous.models import RendezVous, StatutRendezVous, TypeConsultation
from rendezvous.services import creer_rendez_vous


@override_settings(
    SGHL_FRONTEND_URL='http://localhost:5173',
    SGHL_JITSI_DOMAIN='meet.jit.si',
    SGHL_JITSI_ROOM_PREFIX='sghl-visio',
    SGHL_VISIO_EARLY_MINUTES=15,
    SGHL_VISIO_LATE_MINUTES=15,
)
class VisioSessionApiTests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.medecin = User.objects.create_user(
            username='med_visio',
            password='x',
            role=Role.MEDECIN,
            first_name='Alice',
            last_name='Mbemba',
        )
        self.patient = Patient.objects.create(
            numero_dossier='P-VISIO-001',
            nom='Ngoma',
            prenom='Paul',
            date_naissance='1990-01-01',
            sexe=Sexe.MASCULIN,
            consentement_donnees=True,
        )
        self.token = 'demo-visio-token'
        self.rdv = creer_rendez_vous(
            patient=self.patient,
            medecin=self.medecin,
            date_heure=timezone.now() + timedelta(hours=1),
            motif='Consultation visio',
            auteur=self.medecin,
            type_consultation=TypeConsultation.TELECONSULTATION,
        )
        self.rdv.lien_visio = f'http://localhost:5173/visio/{self.token}'
        self.rdv.save(update_fields=['lien_visio', 'updated_at'])

    def test_get_visio_session_success(self):
        response = self.client.get(f'/visio/{self.token}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['patientName'], 'Paul Ngoma')
        self.assertEqual(data['doctorName'], 'Alice Mbemba')
        self.assertEqual(data['room_name'], f'sghl-visio-{self.rdv.id.hex}')
        self.assertEqual(data['jitsi_domain'], 'meet.jit.si')
        self.assertFalse(data['can_join'])

    def test_get_visio_session_within_window(self):
        self.rdv.date_heure = timezone.now() + timedelta(minutes=5)
        self.rdv.save(update_fields=['date_heure', 'updated_at'])
        response = self.client.get(f'/visio/{self.token}/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['can_join'])

    def test_get_visio_session_cancelled(self):
        self.rdv.statut = StatutRendezVous.ANNULE
        self.rdv.date_heure = timezone.now() + timedelta(minutes=5)
        self.rdv.save(update_fields=['statut', 'date_heure', 'updated_at'])
        response = self.client.get(f'/visio/{self.token}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['can_join'])
        self.assertIn('annulée', data['join_message'])

    def test_get_visio_session_not_found(self):
        response = self.client.get('/visio/inconnu/')
        self.assertEqual(response.status_code, 404)

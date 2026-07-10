from datetime import date, datetime, time, timedelta

from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from ninja.testing import TestClient

from accounts.models import Role, User
from accounts.test_helpers import auth_headers
from api.v1.router import api
from patients.models import Patient, Sexe
from rendezvous.models import StatutRendezVous
from rendezvous.models import RendezVous
from rendezvous.rappels import envoyer_rappels_j1, queryset_rappel_j1
from rendezvous.services import (
    RendezVousError,
    annuler_rendez_vous,
    confirmer_rendez_vous,
    creer_rendez_vous,
    get_rendez_vous,
    modifier_rendez_vous,
)


@override_settings(PDF_SIGNING_KEY='test-key')
class RendezVousServiceTests(TestCase):
    def setUp(self):
        self.medecin = User.objects.create_user(
            username='med_rdv',
            password='x',
            role=Role.MEDECIN,
            first_name='Jean',
            last_name='Okemba',
        )
        self.infirmier = User.objects.create_user(username='inf_rdv', password='x', role=Role.INFIRMIER)
        self.patient = Patient.objects.create(
            numero_dossier='P-RDV-001',
            nom='Test',
            prenom='Rdv',
            date_naissance=date(1990, 1, 1),
            sexe=Sexe.MASCULIN,
            consentement_donnees=True,
        )
        self.date_heure = timezone.now() + timedelta(days=2)

    def test_creer_confirmer_annuler(self):
        rdv = creer_rendez_vous(
            patient=self.patient,
            medecin=self.medecin,
            date_heure=self.date_heure,
            motif='Consultation générale',
            auteur=self.infirmier,
        )
        self.assertEqual(rdv.statut, StatutRendezVous.PLANIFIE)

        rdv = confirmer_rendez_vous(rdv=rdv, auteur=self.infirmier, version=rdv.version)
        self.assertEqual(rdv.statut, StatutRendezVous.CONFIRME)

        rdv = annuler_rendez_vous(
            rdv=rdv,
            auteur=self.infirmier,
            version=rdv.version,
            motif_annulation='Patient indisponible',
        )
        self.assertEqual(rdv.statut, StatutRendezVous.ANNULE)

    def test_creneau_indisponible(self):
        creer_rendez_vous(
            patient=self.patient,
            medecin=self.medecin,
            date_heure=self.date_heure,
            motif='Premier créneau',
            auteur=self.infirmier,
        )
        patient2 = Patient.objects.create(
            numero_dossier='P-RDV-002',
            nom='Autre',
            prenom='Patient',
            date_naissance=date(1985, 5, 5),
            sexe=Sexe.FEMININ,
            consentement_donnees=True,
        )
        with self.assertRaises(RendezVousError) as ctx:
            creer_rendez_vous(
                patient=patient2,
                medecin=self.medecin,
                date_heure=self.date_heure,
                motif='Conflit',
                auteur=self.infirmier,
            )
        self.assertEqual(ctx.exception.code, 'creneau_indisponible')


@override_settings(
    PDF_SIGNING_KEY='test-key',
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    EMAIL_NOTIFICATIONS_ENABLED=True,
)
class RendezVousEmailTests(TestCase):
    def setUp(self):
        self.medecin = User.objects.create_user(
            username='med_rdv_mail',
            password='x',
            role=Role.MEDECIN,
            first_name='Marie',
            last_name='Dupont',
        )
        self.infirmier = User.objects.create_user(username='inf_rdv_mail', password='x', role=Role.INFIRMIER)
        self.patient = Patient.objects.create(
            numero_dossier='P-RDV-MAIL',
            nom='Mail',
            prenom='Test',
            date_naissance=date(1990, 1, 1),
            sexe=Sexe.MASCULIN,
            email='patient.rdv@test.local',
            consentement_donnees=True,
        )
        self.date_heure = timezone.now() + timedelta(days=2)

    def test_emails_planifie_confirme_annule(self):
        with self.captureOnCommitCallbacks(execute=True):
            rdv = creer_rendez_vous(
                patient=self.patient,
                medecin=self.medecin,
                date_heure=self.date_heure,
                motif='Contrôle',
                auteur=self.infirmier,
            )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('planifié', mail.outbox[0].subject.lower())
        self.assertEqual(mail.outbox[0].to, ['patient.rdv@test.local'])

        with self.captureOnCommitCallbacks(execute=True):
            rdv = confirmer_rendez_vous(rdv=rdv, auteur=self.infirmier, version=rdv.version)
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn('confirmé', mail.outbox[1].subject.lower())

        with self.captureOnCommitCallbacks(execute=True):
            rdv = annuler_rendez_vous(
                rdv=rdv,
                auteur=self.infirmier,
                version=rdv.version,
                motif_annulation='Report demandé',
            )
        self.assertEqual(len(mail.outbox), 3)
        self.assertIn('annulé', mail.outbox[2].subject.lower())
        self.assertIn('Report demandé', mail.outbox[2].body)

    def test_sans_email_patient_aucun_envoi(self):
        self.patient.email = ''
        self.patient.save(update_fields=['email'])
        with self.captureOnCommitCallbacks(execute=True):
            creer_rendez_vous(
                patient=self.patient,
                medecin=self.medecin,
                date_heure=self.date_heure,
                motif='Sans mail',
                auteur=self.infirmier,
            )
        self.assertEqual(len(mail.outbox), 0)

    def test_email_demande_patient(self):
        compte = User.objects.create_user(
            username='patient_rdv_mail',
            password='x',
            role=Role.PATIENT,
        )
        self.patient.compte_utilisateur = compte
        self.patient.save(update_fields=['compte_utilisateur'])
        mail.outbox.clear()
        with self.captureOnCommitCallbacks(execute=True):
            creer_rendez_vous(
                patient=self.patient,
                medecin=self.medecin,
                date_heure=self.date_heure,
                motif='En ligne',
                auteur=compte,
            )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('demande', mail.outbox[0].subject.lower())


@override_settings(
    PDF_SIGNING_KEY='test-key',
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    EMAIL_NOTIFICATIONS_ENABLED=True,
)
class RendezVousModifierEmailTests(TestCase):
    def setUp(self):
        self.medecin = User.objects.create_user(
            username='med_mod',
            password='x',
            role=Role.MEDECIN,
            first_name='Paul',
            last_name='Martin',
        )
        self.infirmier = User.objects.create_user(username='inf_mod', password='x', role=Role.INFIRMIER)
        self.patient = Patient.objects.create(
            numero_dossier='P-RDV-MOD',
            nom='Mod',
            prenom='Test',
            date_naissance=date(1991, 3, 3),
            sexe=Sexe.MASCULIN,
            email='modif.rdv@test.local',
            consentement_donnees=True,
        )
        self.date_heure = timezone.now() + timedelta(days=4)

    def test_email_reporte_et_modifie(self):
        with self.captureOnCommitCallbacks(execute=True):
            rdv = creer_rendez_vous(
                patient=self.patient,
                medecin=self.medecin,
                date_heure=self.date_heure,
                motif='Consultation',
                auteur=self.infirmier,
            )
        mail.outbox.clear()

        nouvelle_date = self.date_heure + timedelta(days=1)
        with self.captureOnCommitCallbacks(execute=True):
            modifier_rendez_vous(
                rdv=rdv,
                auteur=self.infirmier,
                version=rdv.version,
                date_heure=nouvelle_date,
                motif_modification='Médecin indisponible',
            )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('reporté', mail.outbox[0].subject.lower())

        rdv = get_rendez_vous(rdv.id)
        mail.outbox.clear()
        with self.captureOnCommitCallbacks(execute=True):
            modifier_rendez_vous(
                rdv=rdv,
                auteur=self.infirmier,
                version=rdv.version,
                motif='Bilan complet',
            )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('modifié', mail.outbox[0].subject.lower())


@override_settings(
    PDF_SIGNING_KEY='test-key',
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    EMAIL_NOTIFICATIONS_ENABLED=True,
)
class RendezVousRappelJ1Tests(TestCase):
    def setUp(self):
        self.medecin = User.objects.create_user(
            username='med_rdv_rappel',
            password='x',
            role=Role.MEDECIN,
            first_name='Paul',
            last_name='Martin',
        )
        self.infirmier = User.objects.create_user(username='inf_rdv_rappel', password='x', role=Role.INFIRMIER)
        self.patient = Patient.objects.create(
            numero_dossier='P-RDV-RAPPEL',
            nom='Rappel',
            prenom='J1',
            date_naissance=date(1988, 6, 6),
            sexe=Sexe.FEMININ,
            email='rappel.j1@test.local',
            consentement_donnees=True,
        )
        tz = timezone.get_current_timezone()
        demain = timezone.localdate() + timedelta(days=1)
        self.date_demain = timezone.make_aware(datetime.combine(demain, time(14, 30)), tz)

    def _creer_rdv_demain(self):
        with self.captureOnCommitCallbacks(execute=True):
            return creer_rendez_vous(
                patient=self.patient,
                medecin=self.medecin,
                date_heure=self.date_demain,
                motif='Suivi',
                auteur=self.infirmier,
            )

    def test_rappel_j1_envoi_et_idempotence(self):
        self._creer_rdv_demain()
        mail.outbox.clear()
        self.assertEqual(queryset_rappel_j1().count(), 1)

        stats = envoyer_rappels_j1()
        self.assertEqual(stats['envoyes'], 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('rappel', mail.outbox[0].subject.lower())

        rdv = RendezVous.objects.get(patient=self.patient)
        self.assertIsNotNone(rdv.rappel_j1_envoye_le)

        stats2 = envoyer_rappels_j1()
        self.assertEqual(stats2['envoyes'], 0)
        self.assertEqual(len(mail.outbox), 1)

    def test_rdv_aujourdhui_non_eligible(self):
        tz = timezone.get_current_timezone()
        aujourd_hui = timezone.localdate()
        date_heure = timezone.make_aware(datetime.combine(aujourd_hui, time(16, 0)), tz)
        with self.captureOnCommitCallbacks(execute=True):
            creer_rendez_vous(
                patient=self.patient,
                medecin=self.medecin,
                date_heure=date_heure,
                motif='Aujourd hui',
                auteur=self.infirmier,
            )
        self.assertEqual(queryset_rappel_j1().count(), 0)


class RendezVousAPITests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.medecin = User.objects.create_user(
            username='medecin_rdv_api',
            password='Medecin@SGHL2026',
            role=Role.MEDECIN,
            first_name='Jean',
            last_name='Okemba',
        )
        self.infirmier = User.objects.create_user(
            username='infirmier_rdv',
            password='Infirmier@SGHL2026',
            role=Role.INFIRMIER,
            mfa_enabled=True,
        )
        self.headers = auth_headers(self.infirmier)

        self.patient = Patient.objects.create(
            numero_dossier='P-RDV-API',
            nom='Api',
            prenom='Rdv',
            date_naissance=date(1992, 3, 3),
            sexe=Sexe.MASCULIN,
            consentement_donnees=True,
        )

    def test_workflow_api(self):
        date_heure = (timezone.now() + timedelta(days=3)).isoformat()
        create = self.client.post(
            '/rendez-vous/',
            json={
                'patient_id': str(self.patient.id),
                'medecin_id': self.medecin.id,
                'date_heure': date_heure,
                'motif': 'Bilan annuel',
            },
            headers=self.headers,
        )
        self.assertEqual(create.status_code, 200)
        rdv_id = create.json()['id']
        version = create.json()['version']

        confirm = self.client.post(
            f'/rendez-vous/{rdv_id}/confirmer/',
            json={'version': version},
            headers=self.headers,
        )
        self.assertEqual(confirm.status_code, 200)
        self.assertEqual(confirm.json()['statut'], 'confirme')

        stats = self.client.get('/rendez-vous/stats/', headers=self.headers)
        self.assertEqual(stats.status_code, 200)
        self.assertGreaterEqual(stats.json()['rdv_planifies'], 1)

    def test_semaine_calendrier(self):
        resp = self.client.get('/rendez-vous/semaine/', headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        jours = resp.json()
        self.assertEqual(len(jours), 7)
        self.assertIn('date', jours[0])
        self.assertIn('count', jours[0])

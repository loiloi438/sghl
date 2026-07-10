from datetime import date

from django.test import TestCase
from ninja.testing import TestClient

from accounts.models import Role, User
from accounts.test_helpers import auth_headers
from api.v1.router import api
from facturation.models import Facture, StatutFacture, TarifActe
from facturation.services import generer_facture, valider_facture
from hospitalisation.services import admettre_patient
from logistics.models import Batiment, Chambre, Lit, Service
from patients.models import Patient, Sexe
from prescriptions.services import creer_prescription
from rendezvous.services import creer_rendez_vous
from django.utils import timezone
from datetime import timedelta


class StatistiquesAPITests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.admin = User.objects.create_user(
            username='admin_stats',
            password='Admin@SGHL2026',
            role=Role.ADMIN,
            mfa_enabled=True,
        )
        self.medecin = User.objects.create_user(
            username='med_stats',
            password='Medecin@SGHL2026',
            role=Role.MEDECIN,
            mfa_enabled=True,
        )
        self.headers = auth_headers(self.admin)

        TarifActe.objects.create(code='ADMISSION', libelle='Admission', categorie='sejour', prix_unitaire='10000')
        TarifActe.objects.create(code='SEJOUR_JOUR', libelle='Jour', categorie='sejour', prix_unitaire='5000')

        batiment = Batiment.objects.create(code='B', nom='Bloc')
        service = Service.objects.create(batiment=batiment, code='MED', nom='Médecine')
        chambre = Chambre.objects.create(service=service, numero='101')
        lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient = Patient.objects.create(
            numero_dossier='P-STAT',
            nom='Stat',
            prenom='Test',
            date_naissance=date(1991, 1, 1),
            sexe=Sexe.MASCULIN,
            consentement_donnees=True,
        )

        hosp = admettre_patient(
            patient=self.patient,
            lit=lit,
            motif_admission='Bilan',
            lit_version=lit.version,
        )
        self.prescription = creer_prescription(
            hospitalisation=hosp,
            medecin=self.medecin,
            observations='Suivi',
            codes_cim10=[],
        )
        self.rdv_datetime = timezone.now() + timedelta(hours=2)
        self.rdv = creer_rendez_vous(
            patient=self.patient,
            medecin=self.medecin,
            date_heure=self.rdv_datetime,
            motif='Contrôle',
            auteur=self.admin,
        )
        facture = generer_facture(hospitalisation=hosp, comptable=self.admin)
        self.facture = valider_facture(facture=facture, comptable=self.admin, version=facture.version)

    def test_rapport_et_exports(self):
        today = timezone.localdate()
        start = today.replace(day=1).isoformat()
        end = max(today, self.rdv_datetime.date()).isoformat()
        response = self.client.get(f'/statistiques/rapport/?start_date={start}&end_date={end}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(data['kpis']['admissions'], 1)
        self.assertGreaterEqual(data['kpis']['rendez_vous'], 1)
        self.assertGreaterEqual(data['kpis']['prescriptions'], 1)
        self.assertGreaterEqual(data['kpis']['factures'], 1)
        self.assertGreaterEqual(len(data['evolution_journaliere']), 1)
        self.assertGreaterEqual(len(data['prescriptions_par_statut']), 1)
        self.assertEqual(data['prescriptions_par_statut'][0]['statut'], 'brouillon')

        pdf = self.client.get(f'/statistiques/rapport/pdf/?start_date={start}&end_date={end}', headers=self.headers)
        self.assertEqual(pdf.status_code, 200)
        self.assertIn('application/pdf', pdf.headers.get('Content-Type', ''))
        self.assertTrue(pdf.content.startswith(b'%PDF'))

        csv = self.client.get(f'/statistiques/rapport/csv/?start_date={start}&end_date={end}', headers=self.headers)
        self.assertEqual(csv.status_code, 200)
        self.assertIn('text/csv', csv.headers.get('Content-Type', ''))
        self.assertIn('date,admissions,rendez_vous,prescriptions,factures', csv.content.decode('utf-8').splitlines()[0])
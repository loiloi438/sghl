from datetime import date

from django.test import TestCase
from ninja.testing import TestClient

from accounts.models import Role, User
from accounts.test_helpers import auth_headers
from api.v1.router import api
from hospitalisation.models import StatutHospitalisation
from hospitalisation.services import HospitalisationError, admettre_patient, sortir_patient
from logistics.models import Batiment, Chambre, Lit, Service, StatutLit
from patients.models import Patient, Sexe


class HospitalisationServiceTests(TestCase):
    def setUp(self):
        batiment = Batiment.objects.create(code='A', nom='Principal')
        service = Service.objects.create(batiment=batiment, code='MED', nom='Médecine')
        chambre = Chambre.objects.create(service=service, numero='101')
        self.lit = Lit.objects.create(chambre=chambre, numero='1')
        self.lit2 = Lit.objects.create(chambre=chambre, numero='2')
        self.patient = Patient.objects.create(
            numero_dossier='P-001',
            nom='Test',
            prenom='Patient',
            date_naissance=date(1985, 1, 1),
            sexe=Sexe.MASCULIN,
            consentement_donnees=True,
        )
        self.patient2 = Patient.objects.create(
            numero_dossier='P-002',
            nom='Autre',
            prenom='Patient',
            date_naissance=date(1990, 1, 1),
            sexe=Sexe.FEMININ,
            consentement_donnees=True,
        )

    def test_admission_occupe_le_lit(self):
        hosp = admettre_patient(
            patient=self.patient,
            lit=self.lit,
            motif_admission='Fièvre',
            lit_version=self.lit.version,
        )
        self.lit.refresh_from_db()
        self.assertEqual(hosp.statut, StatutHospitalisation.ACTIVE)
        self.assertEqual(self.lit.statut, StatutLit.OCCUPE)

    def test_admission_refusee_si_lit_occupe(self):
        admettre_patient(
            patient=self.patient,
            lit=self.lit,
            motif_admission='Fièvre',
            lit_version=self.lit.version,
        )
        self.lit.refresh_from_db()
        with self.assertRaises(HospitalisationError) as ctx:
            admettre_patient(
                patient=self.patient2,
                lit=self.lit,
                motif_admission='Douleur',
                lit_version=self.lit.version,
            )
        self.assertEqual(ctx.exception.code, 'lit_indisponible')

    def test_patient_deja_hospitalise(self):
        admettre_patient(
            patient=self.patient,
            lit=self.lit,
            motif_admission='Fièvre',
            lit_version=self.lit.version,
        )
        with self.assertRaises(HospitalisationError) as ctx:
            admettre_patient(
                patient=self.patient,
                lit=self.lit2,
                motif_admission='Autre motif',
                lit_version=self.lit2.version,
            )
        self.assertEqual(ctx.exception.code, 'patient_deja_hospitalise')

    def test_sortie_libere_le_lit(self):
        hosp = admettre_patient(
            patient=self.patient,
            lit=self.lit,
            motif_admission='Fièvre',
            lit_version=self.lit.version,
        )
        sortir_patient(hospitalisation=hosp, hospitalisation_version=hosp.version)
        self.lit.refresh_from_db()
        hosp.refresh_from_db()
        self.assertEqual(hosp.statut, StatutHospitalisation.SORTIE)
        self.assertEqual(self.lit.statut, StatutLit.LIBRE)


class HospitalisationAPITests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.user = User.objects.create_user(
            username='infirmier',
            password='Infirmier@SGHL2026',
            role=Role.INFIRMIER,
            mfa_enabled=True,
        )
        self.headers = auth_headers(self.user)

        batiment = Batiment.objects.create(code='B', nom='Annexe')
        service = Service.objects.create(batiment=batiment, code='CHIR', nom='Chirurgie')
        chambre = Chambre.objects.create(service=service, numero='201')
        self.lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient = Patient.objects.create(
            numero_dossier='P-API-001',
            nom='API',
            prenom='Test',
            date_naissance=date(1995, 6, 10),
            sexe=Sexe.MASCULIN,
            consentement_donnees=True,
        )

    def test_admission_via_api(self):
        response = self.client.post(
            '/hospitalisations/admission/',
            json={
                'patient_id': str(self.patient.id),
                'lit_id': str(self.lit.id),
                'lit_version': self.lit.version,
                'motif_admission': 'Appendicite suspectée',
            },
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['statut'], 'active')
        self.lit.refresh_from_db()
        self.assertEqual(self.lit.statut, StatutLit.OCCUPE)

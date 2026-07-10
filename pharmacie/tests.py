from datetime import date

from django.test import TestCase
from ninja.testing import TestClient

from accounts.models import Role, User
from accounts.test_helpers import auth_headers
from api.v1.router import api
from hospitalisation.services import admettre_patient
from logistics.models import Batiment, Chambre, Lit, Service
from patients.models import Patient, Sexe
from pharmacie.models import MedicamentStock, StatutOrdreDispensation
from pharmacie.services import (
    PharmacieError,
    creer_ordre_dispensation,
    dispenser_ordre,
    preparer_ordre,
)
from prescriptions.models import DiagnosticCIM10
from prescriptions.services import ajouter_ligne, creer_prescription, valider_prescription


class PharmacieServiceTests(TestCase):
    def setUp(self):
        batiment = Batiment.objects.create(code='P', nom='Pharma')
        service = Service.objects.create(batiment=batiment, code='MED', nom='Médecine')
        chambre = Chambre.objects.create(service=service, numero='501')
        self.lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient = Patient.objects.create(
            numero_dossier='P-PH-001',
            nom='Pharma',
            prenom='Test',
            date_naissance=date(1985, 8, 8),
            sexe=Sexe.MASCULIN,
            consentement_donnees=True,
        )
        self.medecin = User.objects.create_user(
            username='medecin_pharma',
            password='Medecin@SGHL2026',
            role=Role.MEDECIN,
        )
        self.pharmacien = User.objects.create_user(
            username='pharmacien_svc',
            password='Pharmacien@SGHL2026',
            role=Role.PHARMACIEN,
        )
        self.hospitalisation = admettre_patient(
            patient=self.patient,
            lit=self.lit,
            motif_admission='Infection',
            lit_version=self.lit.version,
        )
        DiagnosticCIM10.objects.create(code='J06.9', libelle='IVRS')
        MedicamentStock.objects.create(
            code='AMOX500',
            libelle='Amoxicilline 500 mg',
            quantite_stock=10,
        )

    def _prescription_validee(self):
        prescription = creer_prescription(
            hospitalisation=self.hospitalisation,
            medecin=self.medecin,
            codes_cim10=['J06.9'],
        )
        ajouter_ligne(
            prescription=prescription,
            medicament='Amoxicilline',
            posologie='500 mg x3/j',
        )
        valider_prescription(
            prescription=prescription,
            medecin=self.medecin,
            version=prescription.version,
        )
        prescription.refresh_from_db()
        return prescription

    def test_dispensation_decremente_stock_et_verrouille(self):
        prescription = self._prescription_validee()
        ordre = creer_ordre_dispensation(
            prescription=prescription,
            pharmacien=self.pharmacien,
        )
        preparer_ordre(
            ordre=ordre,
            pharmacien=self.pharmacien,
            version=ordre.version,
        )
        ordre.refresh_from_db()
        dispenser_ordre(
            ordre=ordre,
            pharmacien=self.pharmacien,
            version=ordre.version,
        )
        ordre.refresh_from_db()
        stock = MedicamentStock.objects.get(code='AMOX500')

        self.assertEqual(ordre.statut, StatutOrdreDispensation.DISPENSE)
        self.assertTrue(ordre.est_verrouille)
        self.assertEqual(stock.quantite_stock, 9)

    def test_stock_insuffisant_refuse_dispensation(self):
        prescription = self._prescription_validee()
        MedicamentStock.objects.filter(code='AMOX500').update(quantite_stock=0)
        ordre = creer_ordre_dispensation(
            prescription=prescription,
            pharmacien=self.pharmacien,
        )
        with self.assertRaises(PharmacieError) as ctx:
            dispenser_ordre(
                ordre=ordre,
                pharmacien=self.pharmacien,
                version=ordre.version,
            )
        self.assertEqual(ctx.exception.code, 'stock_insuffisant')


class PharmacieAPITests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.medecin = User.objects.create_user(
            username='medecin_api_pharma',
            password='Medecin@SGHL2026',
            role=Role.MEDECIN,
            mfa_enabled=True,
        )
        self.pharmacien = User.objects.create_user(
            username='pharmacien_api',
            password='Pharmacien@SGHL2026',
            role=Role.PHARMACIEN,
            mfa_enabled=True,
        )
        self.headers = auth_headers(self.pharmacien)

        batiment = Batiment.objects.create(code='PH', nom='Bloc')
        service = Service.objects.create(batiment=batiment, code='MED', nom='Médecine')
        chambre = Chambre.objects.create(service=service, numero='601')
        self.lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient = Patient.objects.create(
            numero_dossier='P-PH-API',
            nom='API',
            prenom='Pharma',
            date_naissance=date(1993, 2, 2),
            sexe=Sexe.FEMININ,
            consentement_donnees=True,
        )
        self.hospitalisation = admettre_patient(
            patient=self.patient,
            lit=self.lit,
            motif_admission='Fièvre',
            lit_version=self.lit.version,
        )
        DiagnosticCIM10.objects.create(code='R50.9', libelle='Fièvre')
        MedicamentStock.objects.create(code='PARA1G', libelle='Paracétamol 1 g', quantite_stock=50)

        self.headers_med = auth_headers(self.medecin)

        create_rx = self.client.post(
            f'/hospitalisations/{self.hospitalisation.id}/prescriptions/',
            json={'codes_cim10': ['R50.9'], 'observations': ''},
            headers=self.headers_med,
        )
        rx_id = create_rx.json()['id']
        self.client.post(
            f'/prescriptions/{rx_id}/lignes/',
            json={'medicament': 'Paracétamol', 'posologie': '1g x3/j'},
            headers=self.headers_med,
        )
        self.client.post(
            f'/prescriptions/{rx_id}/valider/',
            json={'version': create_rx.json()['version']},
            headers=self.headers_med,
        )
        self.prescription_id = rx_id

    def test_workflow_dispensation_api(self):
        create_ordre = self.client.post(
            f'/prescriptions/{self.prescription_id}/ordre-dispensation/',
            headers=self.headers,
        )
        self.assertEqual(create_ordre.status_code, 200)
        ordre_id = create_ordre.json()['id']
        version = create_ordre.json()['version']

        prep = self.client.post(
            f'/pharmacie/ordres-dispensation/{ordre_id}/preparer/',
            json={'version': version},
            headers=self.headers,
        )
        self.assertEqual(prep.status_code, 200)
        version = prep.json()['version']

        disp = self.client.post(
            f'/pharmacie/ordres-dispensation/{ordre_id}/dispenser/',
            json={'version': version},
            headers=self.headers,
        )
        self.assertEqual(disp.status_code, 200)
        self.assertEqual(disp.json()['statut'], 'dispense')
        self.assertTrue(disp.json()['est_verrouille'])

        stock_resp = self.client.get('/pharmacie/stock/', headers=self.headers)
        stocks = stock_resp.json()
        if isinstance(stocks, dict) and 'items' in stocks:
            stocks = stocks['items']
        para = next(s for s in stocks if s['code'] == 'PARA1G')
        self.assertEqual(para['quantite_stock'], 49)

from datetime import date

from django.test import TestCase
from ninja.testing import TestClient

from accounts.models import Role, User
from accounts.test_helpers import auth_headers
from api.v1.router import api
from hospitalisation.services import admettre_patient
from laboratoire.models import AnalyseCatalogue, StatutCommandeAnalyse
from laboratoire.services import (
    LaboratoireError,
    creer_commande,
    enregistrer_affectation,
    enregistrer_prelevement,
    publier_commande,
    saisir_resultats,
    valider_commande,
)
from logistics.models import Batiment, Chambre, Lit, Service
from patients.models import Patient, Sexe


class LaboratoireServiceTests(TestCase):
    def setUp(self):
        batiment = Batiment.objects.create(code='L', nom='Labo')
        service = Service.objects.create(batiment=batiment, code='MED', nom='Médecine')
        chambre = Chambre.objects.create(service=service, numero='301')
        self.lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient = Patient.objects.create(
            numero_dossier='P-LAB-001',
            nom='Labo',
            prenom='Test',
            date_naissance=date(1988, 3, 3),
            sexe=Sexe.FEMININ,
            consentement_donnees=True,
        )
        self.medecin = User.objects.create_user(
            username='medecin_lab',
            password='Medecin@SGHL2026',
            role=Role.MEDECIN,
        )
        self.biologiste = User.objects.create_user(
            username='biologiste_lab',
            password='Biologiste@SGHL2026',
            role=Role.BIOLOGISTE,
        )
        self.infirmier = User.objects.create_user(
            username='infirmier_lab',
            password='Infirmier@SGHL2026',
            role=Role.INFIRMIER,
        )
        self.hospitalisation = admettre_patient(
            patient=self.patient,
            lit=self.lit,
            motif_admission='Bilan',
            lit_version=self.lit.version,
        )
        AnalyseCatalogue.objects.create(code='GLY', libelle='Glycémie', unite_reference='g/L')
        AnalyseCatalogue.objects.create(code='NFS', libelle='NFS')

    def _commande_complete(self):
        commande = creer_commande(
            hospitalisation=self.hospitalisation,
            medecin=self.medecin,
            codes_analyses=['GLY', 'NFS'],
        )
        enregistrer_prelevement(
            commande=commande,
            preleveur=self.infirmier,
            type_echantillon='Sang',
            reference_echantillon='ECH-001',
        )
        commande.refresh_from_db()
        enregistrer_affectation(
            commande=commande,
            affectee_a=self.biologiste,
            affectee_par=self.biologiste,
        )
        commande.refresh_from_db()
        lignes = list(commande.lignes.all())
        saisir_resultats(
            commande=commande,
            saisi_par=self.biologiste,
            resultats=[
                {'ligne_id': lignes[0].id, 'valeur': '0,95', 'unite': 'g/L'},
                {'ligne_id': lignes[1].id, 'valeur': 'Normal'},
            ],
        )
        commande.refresh_from_db()
        valider_commande(
            commande=commande,
            biologiste=self.biologiste,
            version=commande.version,
        )
        commande.refresh_from_db()
        return commande

    def test_validation_verrouille_resultats(self):
        commande = self._commande_complete()
        self.assertEqual(commande.statut, StatutCommandeAnalyse.VALIDEE)
        self.assertTrue(commande.est_verrouillee)

        with self.assertRaises(LaboratoireError) as ctx:
            saisir_resultats(
                commande=commande,
                saisi_par=self.biologiste,
                resultats=[{'ligne_id': commande.lignes.first().id, 'valeur': '1,20'}],
            )
        self.assertEqual(ctx.exception.code, 'commande_verrouillee')

    def test_publication_apres_validation(self):
        commande = self._commande_complete()
        publier_commande(
            commande=commande,
            biologiste=self.biologiste,
            version=commande.version,
        )
        commande.refresh_from_db()
        self.assertEqual(commande.statut, StatutCommandeAnalyse.PUBLIEE)


class LaboratoireAPITests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.medecin = User.objects.create_user(
            username='medecin_api_lab',
            password='Medecin@SGHL2026',
            role=Role.MEDECIN,
            mfa_enabled=True,
        )
        self.biologiste = User.objects.create_user(
            username='biologiste_api_lab',
            password='Biologiste@SGHL2026',
            role=Role.BIOLOGISTE,
            mfa_enabled=True,
        )
        self.infirmier = User.objects.create_user(
            username='infirmier_api_lab',
            password='Infirmier@SGHL2026',
            role=Role.INFIRMIER,
            mfa_enabled=True,
        )

        self.headers_med = auth_headers(self.medecin)
        self.headers_bio = auth_headers(self.biologiste)
        self.headers_inf = auth_headers(self.infirmier)

        batiment = Batiment.objects.create(code='LAB', nom='Annexe')
        service = Service.objects.create(batiment=batiment, code='MED', nom='Médecine')
        chambre = Chambre.objects.create(service=service, numero='401')
        self.lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient = Patient.objects.create(
            numero_dossier='P-LAB-API',
            nom='API',
            prenom='Lab',
            date_naissance=date(1992, 6, 6),
            sexe=Sexe.MASCULIN,
            consentement_donnees=True,
        )
        self.hospitalisation = admettre_patient(
            patient=self.patient,
            lit=self.lit,
            motif_admission='Bilan',
            lit_version=self.lit.version,
        )
        AnalyseCatalogue.objects.create(code='CRP', libelle='CRP', unite_reference='mg/L')

    def test_workflow_laboratoire_api(self):
        create_resp = self.client.post(
            f'/hospitalisations/{self.hospitalisation.id}/commandes-analyses/',
            json={'codes_analyses': ['CRP'], 'observations': 'Suspicion infection'},
            headers=self.headers_med,
        )
        self.assertEqual(create_resp.status_code, 200)
        commande_id = create_resp.json()['id']
        version = create_resp.json()['version']

        prelevement_resp = self.client.post(
            f'/commandes-analyses/{commande_id}/prelevement/',
            json={'type_echantillon': 'Sang veineux', 'reference_echantillon': 'E-001'},
            headers=self.headers_inf,
        )
        self.assertEqual(prelevement_resp.status_code, 200)
        version = prelevement_resp.json()['version']

        affectation_resp = self.client.post(
            f'/commandes-analyses/{commande_id}/affectation/',
            json={'affectee_a_id': self.biologiste.id},
            headers=self.headers_bio,
        )
        self.assertEqual(affectation_resp.status_code, 200)
        version = affectation_resp.json()['version']
        ligne_id = affectation_resp.json()['lignes'][0]['id']

        resultats_resp = self.client.post(
            f'/commandes-analyses/{commande_id}/resultats/',
            json={'resultats': [{'ligne_id': ligne_id, 'valeur': '12', 'unite': 'mg/L'}]},
            headers=self.headers_bio,
        )
        self.assertEqual(resultats_resp.status_code, 200)
        self.assertEqual(resultats_resp.json()['statut'], 'resultats_saisis')
        version = resultats_resp.json()['version']

        valider_resp = self.client.post(
            f'/commandes-analyses/{commande_id}/valider/',
            json={'version': version},
            headers=self.headers_bio,
        )
        self.assertEqual(valider_resp.status_code, 200)
        self.assertTrue(valider_resp.json()['est_verrouillee'])
        version = valider_resp.json()['version']

        publier_resp = self.client.post(
            f'/commandes-analyses/{commande_id}/publier/',
            json={'version': version},
            headers=self.headers_bio,
        )
        self.assertEqual(publier_resp.status_code, 200)
        self.assertEqual(publier_resp.json()['statut'], 'publiee')

        retry_resp = self.client.post(
            f'/commandes-analyses/{commande_id}/resultats/',
            json={'resultats': [{'ligne_id': ligne_id, 'valeur': '99'}]},
            headers=self.headers_bio,
        )
        self.assertEqual(retry_resp.status_code, 403)

from datetime import date
from decimal import Decimal

from django.test import TestCase, override_settings
from ninja.testing import TestClient

from accounts.models import Role, User
from accounts.test_helpers import auth_headers
from api.v1.router import api
from documents.models import DocumentSigne, TypeDocument
from documents.services import DocumentError, obtenir_pdf_facture, verifier_document
from facturation.models import StatutFacture, TarifActe
from facturation.services import generer_facture, valider_facture
from hospitalisation.services import admettre_patient
from logistics.models import Batiment, Chambre, Lit, Service
from patients.models import Patient, Sexe


@override_settings(PDF_SIGNING_KEY='test-pdf-signing-key-32bytes!!')
class DocumentServiceTests(TestCase):
    def setUp(self):
        TarifActe.objects.create(
            code='ADMISSION',
            libelle='Admission',
            categorie='sejour',
            prix_unitaire=Decimal('10000'),
        )
        TarifActe.objects.create(
            code='SEJOUR_JOUR',
            libelle='Jour',
            categorie='sejour',
            prix_unitaire=Decimal('5000'),
        )

        batiment = Batiment.objects.create(code='D', nom='Doc')
        service = Service.objects.create(batiment=batiment, code='MED', nom='Médecine')
        chambre = Chambre.objects.create(service=service, numero='901')
        lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient = Patient.objects.create(
            numero_dossier='P-PDF-001',
            nom='Pdf',
            prenom='Test',
            date_naissance=date(1990, 1, 1),
            sexe=Sexe.MASCULIN,
            consentement_donnees=True,
        )
        self.comptable = User.objects.create_user(username='comptable_pdf', password='x', role=Role.COMPTABLE)
        hospitalisation = admettre_patient(
            patient=self.patient,
            lit=lit,
            motif_admission='Bilan',
            lit_version=lit.version,
        )
        self.facture = generer_facture(hospitalisation=hospitalisation, comptable=self.comptable)
        self.facture = valider_facture(
            facture=self.facture,
            comptable=self.comptable,
            version=self.facture.version,
        )

    def test_generer_pdf_facture_et_verifier(self):
        doc = obtenir_pdf_facture(facture=self.facture, demandeur=self.comptable)
        self.assertEqual(doc.type_document, TypeDocument.FACTURE)
        self.assertTrue(doc.fichier.name.endswith('.pdf'))
        self.assertEqual(len(doc.code_verification), 12)

        doc2 = obtenir_pdf_facture(facture=self.facture, demandeur=self.comptable)
        self.assertEqual(doc.id, doc2.id)
        self.assertEqual(DocumentSigne.objects.count(), 1)

        result = verifier_document(code=doc.code_verification)
        self.assertTrue(result['valide'])
        self.assertTrue(result['empreinte_ok'])
        self.assertTrue(result['signature_ok'])

    def test_facture_brouillon_refusee(self):
        facture = self.facture
        facture.statut = StatutFacture.BROUILLON
        facture.save(update_fields=['statut'])
        with self.assertRaises(DocumentError) as ctx:
            obtenir_pdf_facture(facture=facture, demandeur=self.comptable)
        self.assertEqual(ctx.exception.code, 'statut_invalide')


@override_settings(PDF_SIGNING_KEY='test-pdf-signing-key-32bytes!!')
class DocumentAPITests(TestCase):
    def setUp(self):
        TarifActe.objects.create(
            code='ADMISSION',
            libelle='Admission',
            categorie='sejour',
            prix_unitaire=Decimal('10000'),
        )
        TarifActe.objects.create(
            code='SEJOUR_JOUR',
            libelle='Jour',
            categorie='sejour',
            prix_unitaire=Decimal('5000'),
        )

        self.client = TestClient(api)
        self.comptable = User.objects.create_user(
            username='comptable_pdf_api',
            password='Comptable@SGHL2026',
            role=Role.COMPTABLE,
            mfa_enabled=True,
        )
        self.headers = auth_headers(self.comptable)

        batiment = Batiment.objects.create(code='DA', nom='Doc')
        service = Service.objects.create(batiment=batiment, code='MED', nom='Médecine')
        chambre = Chambre.objects.create(service=service, numero='902')
        lit = Lit.objects.create(chambre=chambre, numero='1')
        self.patient = Patient.objects.create(
            numero_dossier='P-PDF-API',
            nom='Api',
            prenom='Pdf',
            date_naissance=date(1988, 2, 2),
            sexe=Sexe.FEMININ,
            consentement_donnees=True,
        )
        hospitalisation = admettre_patient(
            patient=self.patient,
            lit=lit,
            motif_admission='Séjour',
            lit_version=lit.version,
        )
        facture = generer_facture(hospitalisation=hospitalisation, comptable=self.comptable)
        self.facture = valider_facture(
            facture=facture,
            comptable=self.comptable,
            version=facture.version,
        )

    def test_telecharger_pdf_facture(self):
        response = self.client.get(
            f'/facturation/factures/{self.facture.id}/pdf/',
            headers=self.headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('application/pdf', response.headers.get('Content-Type', ''))
        self.assertTrue(response.content.startswith(b'%PDF'))

        doc = DocumentSigne.objects.get(facture=self.facture)
        verify = self.client.get(f'/documents/verifier/{doc.code_verification}/')
        self.assertEqual(verify.status_code, 200)
        self.assertTrue(verify.json()['valide'])

    def test_liste_documents_signes(self):
        doc = obtenir_pdf_facture(facture=self.facture, demandeur=self.comptable)

        response = self.client.get('/documents/', headers=self.headers)
        self.assertEqual(response.status_code, 200)

        items = response.json().get('items', [])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['id'], str(doc.id))
        self.assertEqual(items[0]['download_path'], f'/facturation/factures/{self.facture.id}/pdf/')
        self.assertEqual(items[0]['verification_path'], f'/documents/verifier/{doc.code_verification}/')

    def test_patient_ne_liste_que_ses_documents(self):
        obtenir_pdf_facture(facture=self.facture, demandeur=self.comptable)
        patient_user = User.objects.create_user(
            username='patient_pdf_api',
            password='Patient@SGHL2026',
            role=Role.PATIENT,
        )
        self.patient.compte_utilisateur = patient_user
        self.patient.save(update_fields=['compte_utilisateur'])

        response = self.client.get(
            '/documents/',
            headers=auth_headers(patient_user),
        )

        self.assertEqual(response.status_code, 200)
        items = response.json().get('items', [])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['patient_dossier'], self.patient.numero_dossier)

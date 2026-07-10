import hashlib
import hmac

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from documents.models import DocumentSigne, TypeDocument
from documents.pdf_builder import build_facture_pdf, build_labo_pdf, build_ordonnance_pdf
from facturation.models import Facture, StatutFacture
from laboratoire.models import CommandeAnalyse, StatutCommandeAnalyse
from prescriptions.models import Prescription, StatutPrescription


class DocumentError(Exception):
    def __init__(self, message: str, code: str = 'error'):
        self.message = message
        self.code = code
        super().__init__(message)


def _signing_key() -> bytes:
    key = getattr(settings, 'PDF_SIGNING_KEY', settings.SECRET_KEY)
    return key.encode('utf-8')


def _compute_signature(
    *,
    type_document: str,
    object_id: str,
    empreinte: str,
    signataire_id: str,
    signe_le_iso: str,
) -> str:
    payload = f'{type_document}|{object_id}|{empreinte}|{signataire_id}|{signe_le_iso}'
    return hmac.new(_signing_key(), payload.encode('utf-8'), hashlib.sha256).hexdigest()


def _verification_code(signature_hex: str) -> str:
    return signature_hex[:12].upper()


def _signataire_label(user: User) -> str:
    return f'{user.first_name} {user.last_name}'.strip() or user.username


def _build_and_store(
    *,
    type_document: str,
    signataire: User,
    numero_reference: str,
    build_fn,
    facture=None,
    commande_analyse=None,
    prescription=None,
) -> DocumentSigne:
    signe_le = timezone.now()
    object_id = str(facture.id if facture else commande_analyse.id if commande_analyse else prescription.id)

    doc_id = hashlib.sha256(f'{type_document}:{object_id}'.encode()).hexdigest()[:12].upper()
    pdf_bytes = build_fn(doc_ref=doc_id)
    empreinte = hashlib.sha256(pdf_bytes).hexdigest()
    signature = _compute_signature(
        type_document=type_document,
        object_id=object_id,
        empreinte=empreinte,
        signataire_id=str(signataire.id),
        signe_le_iso=signe_le.isoformat(),
    )
    code_verification = _verification_code(signature)

    doc = DocumentSigne(
        type_document=type_document,
        facture=facture,
        commande_analyse=commande_analyse,
        prescription=prescription,
        empreinte_sha256=empreinte,
        signature=signature,
        code_verification=code_verification,
        signe_par=signataire,
        signe_le=signe_le,
        signataire_nom=_signataire_label(signataire),
        signataire_role=signataire.role,
        numero_reference=numero_reference,
    )
    filename = f'{type_document}_{object_id[:8]}.pdf'
    doc.fichier.save(filename, ContentFile(pdf_bytes), save=False)
    doc.save()
    return doc


@transaction.atomic
def obtenir_pdf_facture(*, facture: Facture, demandeur: User) -> DocumentSigne:
    facture = Facture.objects.select_related(
        'hospitalisation__patient',
        'validee_par',
    ).prefetch_related('lignes').get(pk=facture.pk)

    if facture.statut not in {StatutFacture.VALIDEE, StatutFacture.PAYEE}:
        raise DocumentError(
            'Seule une facture validée ou payée peut être exportée en PDF.',
            code='statut_invalide',
        )

    existing = DocumentSigne.objects.filter(facture=facture).first()
    if existing:
        return existing

    signataire = facture.validee_par or demandeur
    return _build_and_store(
        type_document=TypeDocument.FACTURE,
        signataire=signataire,
        numero_reference=facture.numero_facture or '',
        build_fn=lambda doc_ref: build_facture_pdf(facture, doc_ref=doc_ref),
        facture=facture,
    )


@transaction.atomic
def obtenir_pdf_labo(*, commande: CommandeAnalyse, demandeur: User) -> DocumentSigne:
    commande = CommandeAnalyse.objects.select_related(
        'hospitalisation__patient',
        'medecin',
        'validee_par',
        'publiee_par',
    ).prefetch_related('lignes__resultat').get(pk=commande.pk)

    if commande.statut != StatutCommandeAnalyse.PUBLIEE:
        raise DocumentError(
            'Seule une commande publiée peut être exportée en PDF.',
            code='statut_invalide',
        )

    existing = DocumentSigne.objects.filter(commande_analyse=commande).first()
    if existing:
        return existing

    signataire = commande.publiee_par or commande.validee_par or demandeur
    return _build_and_store(
        type_document=TypeDocument.COMPTE_RENDU_LABO,
        signataire=signataire,
        numero_reference=str(commande.id)[:8].upper(),
        build_fn=lambda doc_ref: build_labo_pdf(commande, doc_ref=doc_ref),
        commande_analyse=commande,
    )


@transaction.atomic
def obtenir_pdf_ordonnance(*, prescription: Prescription, demandeur: User) -> DocumentSigne:
    prescription = Prescription.objects.select_related(
        'hospitalisation__patient',
        'medecin',
        'validee_par',
    ).prefetch_related('diagnostics', 'lignes').get(pk=prescription.pk)

    if prescription.statut != StatutPrescription.VALIDEE:
        raise DocumentError(
            'Seule une ordonnance validée peut être exportée en PDF.',
            code='statut_invalide',
        )

    existing = DocumentSigne.objects.filter(prescription=prescription).first()
    if existing:
        return existing

    signataire = prescription.validee_par or prescription.medecin or demandeur
    return _build_and_store(
        type_document=TypeDocument.ORDONNANCE,
        signataire=signataire,
        numero_reference=str(prescription.id)[:8].upper(),
        build_fn=lambda doc_ref: build_ordonnance_pdf(prescription, doc_ref=doc_ref),
        prescription=prescription,
    )


def verifier_document(*, code: str) -> dict:
    doc = DocumentSigne.objects.filter(code_verification=code.upper()).first()
    if doc is None:
        raise DocumentError('Document introuvable pour ce code.', code='not_found')

    if not doc.fichier:
        raise DocumentError('Fichier PDF absent.', code='fichier_absent')

    with doc.fichier.open('rb') as f:
        content = f.read()

    empreinte_actuelle = hashlib.sha256(content).hexdigest()
    empreinte_ok = empreinte_actuelle == doc.empreinte_sha256
    signature_attendue = _compute_signature(
        type_document=doc.type_document,
        object_id=str(
            doc.facture_id or doc.commande_analyse_id or doc.prescription_id
        ),
        empreinte=doc.empreinte_sha256,
        signataire_id=str(doc.signe_par_id),
        signe_le_iso=doc.signe_le.isoformat(),
    )
    signature_ok = hmac.compare_digest(signature_attendue, doc.signature)

    return {
        'valide': empreinte_ok and signature_ok,
        'empreinte_ok': empreinte_ok,
        'signature_ok': signature_ok,
        'type_document': doc.type_document,
        'numero_reference': doc.numero_reference,
        'signataire_nom': doc.signataire_nom,
        'signataire_role': doc.signataire_role,
        'signe_le': doc.signe_le,
        'code_verification': doc.code_verification,
    }


def lire_contenu_pdf(document: DocumentSigne) -> bytes:
    with document.fichier.open('rb') as f:
        return f.read()

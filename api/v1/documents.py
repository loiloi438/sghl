from datetime import datetime
from uuid import UUID

from django.http import HttpResponse
from django.db.models import Q
from ninja import Router, Schema
from ninja.pagination import paginate
from ninja.errors import HttpError

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from audit.services import get_client_ip, log_audit
from documents.pdf_builder import build_recu_pdf
from documents.services import (
    DocumentError,
    lire_contenu_pdf,
    obtenir_pdf_facture,
    obtenir_pdf_labo,
    obtenir_pdf_ordonnance,
    verifier_document,
)
from facturation.models import Facture, StatutFacture
from laboratoire.models import CommandeAnalyse
from patients.models import Patient
from prescriptions.models import Prescription
from documents.models import DocumentSigne, TypeDocument

router = Router(tags=['Documents'])
jwt_auth = JWTAuth()


def _handle_error(exc: DocumentError):
    status_map = {
        'not_found': 404,
        'statut_invalide': 400,
        'acces_refuse': 403,
        'fichier_absent': 404,
    }
    raise HttpError(status_map.get(exc.code, 400), exc.message)


def _pdf_response(content: bytes, filename: str) -> HttpResponse:
    response = HttpResponse(content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def _check_patient_access(user: User, patient_id: UUID):
    if user.role == Role.PATIENT:
        patient = Patient.objects.filter(compte_utilisateur=user).first()
        if patient is None or patient.id != patient_id:
            raise HttpError(403, 'Accès refusé.')


class VerificationOut(Schema):
    valide: bool
    empreinte_ok: bool
    signature_ok: bool
    type_document: str
    numero_reference: str
    signataire_nom: str
    signataire_role: str
    signe_le: datetime
    code_verification: str


class DocumentOut(Schema):
    id: UUID
    type_document: str
    type_label: str
    numero_reference: str
    signataire_nom: str
    signataire_role: str
    signe_le: datetime
    code_verification: str
    patient_nom: str | None = None
    patient_dossier: str | None = None
    download_path: str
    verification_path: str


def _document_patient(document: DocumentSigne):
    if document.facture_id and document.facture and document.facture.hospitalisation_id:
        return document.facture.hospitalisation.patient
    if document.commande_analyse_id and document.commande_analyse and document.commande_analyse.hospitalisation_id:
        return document.commande_analyse.hospitalisation.patient
    if document.prescription_id and document.prescription and document.prescription.hospitalisation_id:
        return document.prescription.hospitalisation.patient
    return None


def _download_path(document: DocumentSigne) -> str:
    if document.facture_id:
        return f'/facturation/factures/{document.facture_id}/pdf/'
    if document.commande_analyse_id:
        return f'/commandes-analyses/{document.commande_analyse_id}/pdf/'
    if document.prescription_id:
        return f'/prescriptions/{document.prescription_id}/pdf/'
    return f'/media/{document.fichier.name}'


def _documents_q(search: str | None):
    if not search:
        return Q()
    return (
        Q(numero_reference__icontains=search)
        | Q(code_verification__icontains=search)
        | Q(signataire_nom__icontains=search)
        | Q(signataire_role__icontains=search)
        | Q(facture__hospitalisation__patient__numero_dossier__icontains=search)
        | Q(facture__hospitalisation__patient__nom__icontains=search)
        | Q(facture__hospitalisation__patient__prenom__icontains=search)
        | Q(commande_analyse__hospitalisation__patient__numero_dossier__icontains=search)
        | Q(commande_analyse__hospitalisation__patient__nom__icontains=search)
        | Q(commande_analyse__hospitalisation__patient__prenom__icontains=search)
        | Q(prescription__hospitalisation__patient__numero_dossier__icontains=search)
        | Q(prescription__hospitalisation__patient__nom__icontains=search)
        | Q(prescription__hospitalisation__patient__prenom__icontains=search)
    )


@router.get('/documents/verifier/{code}/', response=VerificationOut)
def verifier_document_endpoint(request, code: str):
    try:
        result = verifier_document(code=code)
    except DocumentError as exc:
        _handle_error(exc)
    return VerificationOut(**result)


@router.get('/documents/', response=list[DocumentOut], auth=jwt_auth)
@paginate
def list_documents(request, search: str | None = None, type_document: str | None = None):
    qs = (
        DocumentSigne.objects.select_related(
            'facture__hospitalisation__patient',
            'commande_analyse__hospitalisation__patient',
            'prescription__hospitalisation__patient',
            'signe_par',
        )
        .all()
        .order_by('-signe_le')
    )
    qs = qs.filter(_documents_q(search))
    if type_document:
        qs = qs.filter(type_document=type_document)

    out = []
    for document in qs:
        patient = _document_patient(document)
        out.append(
            DocumentOut(
                id=document.id,
                type_document=document.type_document,
                type_label=TypeDocument(document.type_document).label,
                numero_reference=document.numero_reference,
                signataire_nom=document.signataire_nom,
                signataire_role=document.signataire_role,
                signe_le=document.signe_le,
                code_verification=document.code_verification,
                patient_nom=(f'{patient.prenom} {patient.nom}' if patient else None),
                patient_dossier=(patient.numero_dossier if patient else None),
                download_path=_download_path(document),
                verification_path=f'/documents/verifier/{document.code_verification}/',
            )
        )
    return out


@router.get('/facturation/factures/{facture_id}/pdf/', auth=jwt_auth)
def telecharger_facture_pdf(request, facture_id: UUID):
    roles_ok = {Role.ADMIN, Role.COMPTABLE, Role.SECRETAIRE, Role.MEDECIN, Role.PATIENT}
    if request.auth.role not in roles_ok:
        raise HttpError(403, 'Accès refusé.')
    try:
        facture = Facture.objects.select_related('hospitalisation__patient').get(id=facture_id)
        _check_patient_access(request.auth, facture.hospitalisation.patient_id)
        document = obtenir_pdf_facture(facture=facture, demandeur=request.auth)
    except Facture.DoesNotExist:
        raise HttpError(404, 'Facture introuvable.')
    except DocumentError as exc:
        _handle_error(exc)

    content = lire_contenu_pdf(document)
    log_audit(
        user=request.auth,
        action='READ',
        model_name='DocumentSigne',
        object_id=document.id,
        new_value={'type': 'facture', 'facture_id': str(facture_id)},
        ip_address=get_client_ip(request),
    )
    filename = f'{facture.numero_facture or facture_id}.pdf'
    return _pdf_response(content, filename)


@router.get('/facturation/factures/{facture_id}/recu/', auth=jwt_auth)
def telecharger_recu_pdf(request, facture_id: UUID):
    roles_ok = {Role.ADMIN, Role.COMPTABLE, Role.SECRETAIRE, Role.MEDECIN, Role.PATIENT}
    if request.auth.role not in roles_ok:
        raise HttpError(403, 'Accès refusé.')
    try:
        facture = Facture.objects.select_related('hospitalisation__patient', 'validee_par').get(
            id=facture_id,
        )
        _check_patient_access(request.auth, facture.hospitalisation.patient_id)
    except Facture.DoesNotExist:
        raise HttpError(404, 'Facture introuvable.')
    if facture.statut not in {StatutFacture.PAYEE, StatutFacture.PARTIELLEMENT_PAYEE}:
        raise HttpError(400, 'Reçu disponible uniquement après un paiement enregistré.')
    doc_ref = f'RECU-{facture.numero_facture or facture_id}'
    content = build_recu_pdf(facture, doc_ref=doc_ref)
    log_audit(
        user=request.auth,
        action='READ',
        model_name='Facture',
        object_id=facture.id,
        new_value={'type': 'recu', 'facture_id': str(facture_id)},
        ip_address=get_client_ip(request),
    )
    filename = f'recu-{facture.numero_facture or facture_id}.pdf'
    return _pdf_response(content, filename)


@router.get('/commandes-analyses/{commande_id}/pdf/', auth=jwt_auth)
def telecharger_labo_pdf(request, commande_id: UUID):
    roles_ok = {Role.ADMIN, Role.MEDECIN, Role.BIOLOGISTE, Role.INFIRMIER, Role.PATIENT}
    if request.auth.role not in roles_ok:
        raise HttpError(403, 'Accès refusé.')
    try:
        commande = CommandeAnalyse.objects.select_related('hospitalisation__patient').get(id=commande_id)
        _check_patient_access(request.auth, commande.hospitalisation.patient_id)
        document = obtenir_pdf_labo(commande=commande, demandeur=request.auth)
    except CommandeAnalyse.DoesNotExist:
        raise HttpError(404, 'Commande introuvable.')
    except DocumentError as exc:
        _handle_error(exc)

    content = lire_contenu_pdf(document)
    log_audit(
        user=request.auth,
        action='READ',
        model_name='DocumentSigne',
        object_id=document.id,
        new_value={'type': 'labo', 'commande_id': str(commande_id)},
        ip_address=get_client_ip(request),
    )
    return _pdf_response(content, f'labo_{commande_id}.pdf')


@router.get('/prescriptions/{prescription_id}/pdf/', auth=jwt_auth)
def telecharger_ordonnance_pdf(request, prescription_id: UUID):
    roles_ok = {Role.ADMIN, Role.MEDECIN, Role.PHARMACIEN, Role.PATIENT}
    if request.auth.role not in roles_ok:
        raise HttpError(403, 'Accès refusé.')
    try:
        prescription = Prescription.objects.select_related('hospitalisation__patient').get(id=prescription_id)
        _check_patient_access(request.auth, prescription.hospitalisation.patient_id)
        document = obtenir_pdf_ordonnance(prescription=prescription, demandeur=request.auth)
    except Prescription.DoesNotExist:
        raise HttpError(404, 'Prescription introuvable.')
    except DocumentError as exc:
        _handle_error(exc)

    content = lire_contenu_pdf(document)
    log_audit(
        user=request.auth,
        action='READ',
        model_name='DocumentSigne',
        object_id=document.id,
        new_value={'type': 'ordonnance', 'prescription_id': str(prescription_id)},
        ip_address=get_client_ip(request),
    )
    return _pdf_response(content, f'ordonnance_{prescription_id}.pdf')

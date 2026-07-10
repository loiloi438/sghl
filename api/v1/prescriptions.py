from datetime import datetime
from typing import Optional
from uuid import UUID

from django.db.models import Q
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from audit.services import get_client_ip, log_audit
from prescriptions.models import DiagnosticCIM10, LignePrescription, Prescription, StatutPrescription
from prescriptions.services import (
    PrescriptionError,
    ajouter_ligne,
    creer_prescription,
    get_hospitalisation_active,
    get_prescription,
    get_prescription_modifiable,
    _ajouter_diagnostics,
    valider_prescription,
)

router = Router(tags=['Prescriptions'])
jwt_auth = JWTAuth()

ROLES_LECTURE = {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER, Role.PHARMACIEN, Role.BIOLOGISTE}
ROLES_ECRITURE = {Role.ADMIN, Role.MEDECIN}


def _check_read(user: User):
    if user.role not in ROLES_LECTURE:
        raise HttpError(403, 'Accès refusé.')


def _check_write(user: User):
    if user.role not in ROLES_ECRITURE:
        raise HttpError(403, 'Accès refusé.')


def _handle_error(exc: PrescriptionError):
    status_map = {
        'not_found': 404,
        'version_conflict': 409,
        'prescription_verrouillee': 403,
        'acces_refuse': 403,
    }
    raise HttpError(status_map.get(exc.code, 400), exc.message)


class DiagnosticCIM10Out(Schema):
    code: str
    libelle: str


class DiagnosticOut(Schema):
    code_cim10: str
    libelle: str


class LigneOut(Schema):
    id: UUID
    medicament: str
    posologie: str
    duree_traitement: str
    voie_administration: str
    instructions: str
    ordre: int


class PrescriptionOut(Schema):
    id: UUID
    hospitalisation_id: UUID
    patient_id: UUID
    numero_dossier: str
    medecin_id: int
    medecin_nom: str
    statut: str
    observations: str
    diagnostics: list[DiagnosticOut]
    lignes: list[LigneOut]
    validee_le: Optional[datetime]
    validee_par_id: Optional[int]
    version: int
    est_verrouillee: bool
    created_at: datetime


class PrescriptionIn(Schema):
    observations: str = ''
    codes_cim10: list[str] = []


class PrescriptionUpdateIn(Schema):
    observations: Optional[str] = None
    codes_cim10: Optional[list[str]] = None
    version: int


class LigneIn(Schema):
    medicament: str
    posologie: str
    duree_traitement: str = ''
    voie_administration: str = 'orale'
    instructions: str = ''
    ordre: int = 1


class ValiderIn(Schema):
    version: int


def _serialize_prescription(p: Prescription) -> PrescriptionOut:
    patient = p.hospitalisation.patient
    medecin = p.medecin
    return PrescriptionOut(
        id=p.id,
        hospitalisation_id=p.hospitalisation_id,
        patient_id=patient.id,
        numero_dossier=patient.numero_dossier,
        medecin_id=medecin.id,
        medecin_nom=f'{medecin.first_name} {medecin.last_name}'.strip() or medecin.username,
        statut=p.statut,
        observations=p.observations,
        diagnostics=[
            DiagnosticOut(code_cim10=d.code_cim10, libelle=d.libelle)
            for d in p.diagnostics.all()
        ],
        lignes=[
            LigneOut(
                id=l.id,
                medicament=l.medicament,
                posologie=l.posologie,
                duree_traitement=l.duree_traitement,
                voie_administration=l.voie_administration,
                instructions=l.instructions,
                ordre=l.ordre,
            )
            for l in p.lignes.all()
        ],
        validee_le=p.validee_le,
        validee_par_id=p.validee_par_id,
        version=p.version,
        est_verrouillee=p.est_verrouillee,
        created_at=p.created_at,
    )


def _load_prescription(prescription_id: UUID) -> Prescription:
    return Prescription.objects.select_related(
        'hospitalisation__patient',
        'medecin',
        'validee_par',
    ).prefetch_related('diagnostics', 'lignes').get(id=prescription_id)


@router.get('/diagnostics-cim10/', response=list[DiagnosticCIM10Out], auth=jwt_auth)
@paginate
def list_diagnostics_cim10(request, search: str = ''):
    _check_read(request.auth)
    qs = DiagnosticCIM10.objects.filter(actif=True)
    if search:
        qs = qs.filter(Q(code__icontains=search) | Q(libelle__icontains=search))
    return [DiagnosticCIM10Out(code=d.code, libelle=d.libelle) for d in qs]


@router.get(
    '/hospitalisations/{hospitalisation_id}/prescriptions/',
    response=list[PrescriptionOut],
    auth=jwt_auth,
)
@paginate
def list_prescriptions_hospitalisation(request, hospitalisation_id: UUID):
    _check_read(request.auth)
    qs = Prescription.objects.filter(
        hospitalisation_id=hospitalisation_id,
    ).select_related(
        'hospitalisation__patient',
        'medecin',
    ).prefetch_related('diagnostics', 'lignes')
    return [_serialize_prescription(p) for p in qs]


@router.post(
    '/hospitalisations/{hospitalisation_id}/prescriptions/',
    response=PrescriptionOut,
    auth=jwt_auth,
)
def create_prescription(request, hospitalisation_id: UUID, payload: PrescriptionIn):
    _check_write(request.auth)
    try:
        hospitalisation = get_hospitalisation_active(hospitalisation_id)
        prescription = creer_prescription(
            hospitalisation=hospitalisation,
            medecin=request.auth,
            observations=payload.observations,
            codes_cim10=payload.codes_cim10 or None,
        )
    except PrescriptionError as exc:
        _handle_error(exc)

    prescription = _load_prescription(prescription.id)
    data = _serialize_prescription(prescription)
    log_audit(
        user=request.auth,
        action='CREATE',
        model_name='Prescription',
        object_id=prescription.id,
        new_value=data.model_dump(),
        ip_address=get_client_ip(request),
    )
    return data


@router.get('/prescriptions/{prescription_id}/', response=PrescriptionOut, auth=jwt_auth)
def get_prescription_detail(request, prescription_id: UUID):
    _check_read(request.auth)
    try:
        prescription = _load_prescription(prescription_id)
    except Prescription.DoesNotExist:
        raise HttpError(404, 'Prescription introuvable.')
    return _serialize_prescription(prescription)


@router.patch('/prescriptions/{prescription_id}/', response=PrescriptionOut, auth=jwt_auth)
def update_prescription(request, prescription_id: UUID, payload: PrescriptionUpdateIn):
    _check_write(request.auth)
    try:
        prescription = get_prescription_modifiable(prescription_id)
    except PrescriptionError as exc:
        _handle_error(exc)

    if prescription.version != payload.version:
        raise HttpError(409, 'Conflit de version : rechargez et réessayez.')

    old_data = _serialize_prescription(
        _load_prescription(prescription.id)
    ).model_dump()

    if payload.observations is not None:
        prescription.observations = payload.observations

    if payload.codes_cim10 is not None:
        prescription.diagnostics.all().delete()
        try:
            _ajouter_diagnostics(prescription, payload.codes_cim10)
        except PrescriptionError as exc:
            _handle_error(exc)

    prescription.bump_version()
    prescription.save(update_fields=['observations', 'version', 'updated_at'])

    prescription = _load_prescription(prescription.id)
    new_data = _serialize_prescription(prescription)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='Prescription',
        object_id=prescription.id,
        old_value=old_data,
        new_value=new_data.model_dump(),
        ip_address=get_client_ip(request),
    )
    return new_data


@router.post('/prescriptions/{prescription_id}/lignes/', response=LigneOut, auth=jwt_auth)
def add_ligne(request, prescription_id: UUID, payload: LigneIn):
    _check_write(request.auth)
    try:
        prescription = get_prescription_modifiable(prescription_id)
        ligne = ajouter_ligne(
            prescription=prescription,
            medicament=payload.medicament,
            posologie=payload.posologie,
            duree_traitement=payload.duree_traitement,
            voie_administration=payload.voie_administration,
            instructions=payload.instructions,
            ordre=payload.ordre,
        )
    except PrescriptionError as exc:
        _handle_error(exc)

    log_audit(
        user=request.auth,
        action='CREATE',
        model_name='LignePrescription',
        object_id=ligne.id,
        new_value=payload.model_dump(),
        ip_address=get_client_ip(request),
    )
    return LigneOut(
        id=ligne.id,
        medicament=ligne.medicament,
        posologie=ligne.posologie,
        duree_traitement=ligne.duree_traitement,
        voie_administration=ligne.voie_administration,
        instructions=ligne.instructions,
        ordre=ligne.ordre,
    )


@router.post('/prescriptions/{prescription_id}/valider/', response=PrescriptionOut, auth=jwt_auth)
def valider_prescription_endpoint(request, prescription_id: UUID, payload: ValiderIn):
    _check_write(request.auth)
    try:
        prescription = get_prescription(prescription_id)
        prescription = valider_prescription(
            prescription=prescription,
            medecin=request.auth,
            version=payload.version,
        )
    except PrescriptionError as exc:
        _handle_error(exc)

    prescription = _load_prescription(prescription.id)
    data = _serialize_prescription(prescription)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='Prescription',
        object_id=prescription.id,
        new_value={**data.model_dump(), 'event': 'validation'},
        ip_address=get_client_ip(request),
    )
    return data

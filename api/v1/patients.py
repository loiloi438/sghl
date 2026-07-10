from datetime import date
from typing import Optional
from uuid import UUID

from django.db.models import Q
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from audit.services import get_client_ip, log_audit
from patients.models import Patient, Sexe

router = Router(tags=['Patients'])
jwt_auth = JWTAuth()

ROLES_LECTURE = {
    Role.ADMIN,
    Role.MEDECIN,
    Role.INFIRMIER,
    Role.BIOLOGISTE,
    Role.PHARMACIEN,
    Role.COMPTABLE,
}
ROLES_ECRITURE = {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER}


class PatientIn(Schema):
    numero_dossier: str
    nom: str
    prenom: str
    date_naissance: date
    sexe: str
    telephone: str = ''
    email: str = ''
    adresse: str = ''
    consentement_donnees: bool = False


class PatientOut(Schema):
    id: UUID
    numero_dossier: str
    nom: str
    prenom: str
    date_naissance: date
    sexe: str
    telephone: str
    email: str
    adresse: str
    consentement_donnees: bool
    version: int


class PatientUpdateIn(Schema):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    date_naissance: Optional[date] = None
    sexe: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    adresse: Optional[str] = None
    consentement_donnees: Optional[bool] = None
    version: int


def _serialize_patient(patient: Patient) -> PatientOut:
    return PatientOut(
        id=patient.id,
        numero_dossier=patient.numero_dossier,
        nom=patient.nom,
        prenom=patient.prenom,
        date_naissance=patient.date_naissance,
        sexe=patient.sexe,
        telephone=patient.telephone,
        email=patient.email,
        adresse=patient.adresse,
        consentement_donnees=patient.consentement_donnees,
        version=patient.version,
    )


def _check_read_access(user: User):
    if user.role == Role.PATIENT:
        raise HttpError(403, 'Accès refusé.')
    if user.role not in ROLES_LECTURE:
        raise HttpError(403, 'Accès refusé.')


def _check_write_access(user: User):
    if user.role not in ROLES_ECRITURE:
        raise HttpError(403, 'Accès refusé.')


@router.get('/patients/', response=list[PatientOut], auth=jwt_auth)
@paginate
def list_patients(request, search: str = ''):
    _check_read_access(request.auth)
    qs = Patient.objects.all()
    if search:
        qs = qs.filter(
            Q(numero_dossier__icontains=search)
            | Q(nom__icontains=search)
            | Q(prenom__icontains=search)
        )
    return [_serialize_patient(p) for p in qs]


@router.get('/patients/{patient_id}/', response=PatientOut, auth=jwt_auth)
def get_patient(request, patient_id: UUID):
    _check_read_access(request.auth)
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        raise HttpError(404, 'Patient introuvable.')
    return _serialize_patient(patient)


@router.post('/patients/', response=PatientOut, auth=jwt_auth)
def create_patient(request, payload: PatientIn):
    _check_write_access(request.auth)
    if payload.sexe not in Sexe.values:
        raise HttpError(400, 'Sexe invalide.')
    if Patient.objects.filter(numero_dossier=payload.numero_dossier).exists():
        raise HttpError(400, 'Ce numéro de dossier existe déjà.')

    patient = Patient.objects.create(
        numero_dossier=payload.numero_dossier,
        nom=payload.nom,
        prenom=payload.prenom,
        date_naissance=payload.date_naissance,
        sexe=payload.sexe,
        telephone=payload.telephone,
        email=payload.email,
        adresse=payload.adresse,
        consentement_donnees=payload.consentement_donnees,
    )
    data = _serialize_patient(patient)
    log_audit(
        user=request.auth,
        action='CREATE',
        model_name='Patient',
        object_id=patient.id,
        new_value=data.model_dump(),
        ip_address=get_client_ip(request),
    )
    return data


@router.patch('/patients/{patient_id}/', response=PatientOut, auth=jwt_auth)
def update_patient(request, patient_id: UUID, payload: PatientUpdateIn):
    _check_write_access(request.auth)
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        raise HttpError(404, 'Patient introuvable.')

    if patient.version != payload.version:
        raise HttpError(409, 'Conflit de version : rechargez le patient et réessayez.')

    old_data = _serialize_patient(patient).model_dump()
    update_fields = []

    for field in ('nom', 'prenom', 'date_naissance', 'sexe', 'telephone', 'email', 'adresse', 'consentement_donnees'):
        value = getattr(payload, field)
        if value is not None:
            if field == 'sexe' and value not in Sexe.values:
                raise HttpError(400, 'Sexe invalide.')
            setattr(patient, field, value)
            update_fields.append(field)

    patient.bump_version()
    update_fields.append('version')
    patient.save(update_fields=update_fields + ['updated_at'])

    new_data = _serialize_patient(patient)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='Patient',
        object_id=patient.id,
        old_value=old_data,
        new_value=new_data.model_dump(),
        ip_address=get_client_ip(request),
    )
    return new_data

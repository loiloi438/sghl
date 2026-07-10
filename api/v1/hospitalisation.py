from datetime import date, datetime
from typing import Optional
from uuid import UUID

from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from audit.services import get_client_ip, log_audit
from hospitalisation.models import Hospitalisation, StatutHospitalisation
from hospitalisation.services import HospitalisationError, admettre_patient, sortir_patient
from logistics.models import Lit
from patients.models import Patient

router = Router(tags=['Hospitalisation'])
jwt_auth = JWTAuth()

ROLES_LECTURE = {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER, Role.BIOLOGISTE}
ROLES_ADMISSION = {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER}
ROLES_SORTIE = {Role.ADMIN, Role.MEDECIN}


class HospitalisationOut(Schema):
    id: UUID
    patient_id: UUID
    patient_nom: str
    patient_prenom: str
    numero_dossier: str
    lit_id: UUID
    lit_numero: str
    chambre_numero: str
    service_code: str
    batiment_code: str
    medecin_referent_id: Optional[int]
    motif_admission: str
    date_admission: datetime
    date_sortie_prevue: Optional[date]
    date_sortie_effective: Optional[datetime]
    statut: str
    version: int


class AdmissionIn(Schema):
    patient_id: UUID
    lit_id: UUID
    lit_version: int
    motif_admission: str
    medecin_referent_id: Optional[int] = None
    date_sortie_prevue: Optional[date] = None


class SortieIn(Schema):
    version: int


def _check_read(user: User):
    if user.role not in ROLES_LECTURE:
        raise HttpError(403, 'Accès refusé.')


def _check_admission(user: User):
    if user.role not in ROLES_ADMISSION:
        raise HttpError(403, 'Accès refusé.')


def _check_sortie(user: User):
    if user.role not in ROLES_SORTIE:
        raise HttpError(403, 'Accès refusé.')


def _serialize_hospitalisation(h: Hospitalisation) -> HospitalisationOut:
    lit = h.lit
    patient = h.patient
    return HospitalisationOut(
        id=h.id,
        patient_id=patient.id,
        patient_nom=patient.nom,
        patient_prenom=patient.prenom,
        numero_dossier=patient.numero_dossier,
        lit_id=lit.id,
        lit_numero=lit.numero,
        chambre_numero=lit.chambre.numero,
        service_code=lit.chambre.service.code,
        batiment_code=lit.chambre.service.batiment.code,
        medecin_referent_id=h.medecin_referent_id,
        motif_admission=h.motif_admission,
        date_admission=h.date_admission,
        date_sortie_prevue=h.date_sortie_prevue,
        date_sortie_effective=h.date_sortie_effective,
        statut=h.statut,
        version=h.version,
    )


def _handle_service_error(exc: HospitalisationError):
    status = 409 if exc.code == 'version_conflict' else 400
    raise HttpError(status, exc.message)


@router.get('/hospitalisations/', response=list[HospitalisationOut], auth=jwt_auth)
@paginate
def list_hospitalisations(request, statut: Optional[str] = None):
    _check_read(request.auth)
    qs = Hospitalisation.objects.select_related(
        'patient',
        'lit__chambre__service__batiment',
    )
    if statut:
        qs = qs.filter(statut=statut)
    return [_serialize_hospitalisation(h) for h in qs]


@router.get('/hospitalisations/actives/', response=list[HospitalisationOut], auth=jwt_auth)
@paginate
def list_hospitalisations_actives(request):
    _check_read(request.auth)
    qs = Hospitalisation.objects.filter(statut=StatutHospitalisation.ACTIVE).select_related(
        'patient',
        'lit__chambre__service__batiment',
    )
    return [_serialize_hospitalisation(h) for h in qs]


@router.post('/hospitalisations/admission/', response=HospitalisationOut, auth=jwt_auth)
def creer_admission(request, payload: AdmissionIn):
    _check_admission(request.auth)
    try:
        patient = Patient.objects.get(id=payload.patient_id)
    except Patient.DoesNotExist:
        raise HttpError(404, 'Patient introuvable.')
    try:
        lit = Lit.objects.get(id=payload.lit_id)
    except Lit.DoesNotExist:
        raise HttpError(404, 'Lit introuvable.')

    medecin = None
    if payload.medecin_referent_id:
        try:
            medecin = User.objects.get(id=payload.medecin_referent_id, role=Role.MEDECIN)
        except User.DoesNotExist:
            raise HttpError(400, 'Médecin référent introuvable.')

    try:
        hospitalisation = admettre_patient(
            patient=patient,
            lit=lit,
            motif_admission=payload.motif_admission,
            medecin_referent=medecin,
            date_sortie_prevue=payload.date_sortie_prevue,
            lit_version=payload.lit_version,
        )
    except HospitalisationError as exc:
        _handle_service_error(exc)

    hospitalisation = Hospitalisation.objects.select_related(
        'patient',
        'lit__chambre__service__batiment',
    ).get(id=hospitalisation.id)
    data = _serialize_hospitalisation(hospitalisation)
    log_audit(
        user=request.auth,
        action='CREATE',
        model_name='Hospitalisation',
        object_id=hospitalisation.id,
        new_value=data.model_dump(),
        ip_address=get_client_ip(request),
    )
    return data


@router.get('/hospitalisations/{hospitalisation_id}/', response=HospitalisationOut, auth=jwt_auth)
def get_hospitalisation(request, hospitalisation_id: UUID):
    _check_read(request.auth)
    try:
        h = Hospitalisation.objects.select_related(
            'patient',
            'lit__chambre__service__batiment',
        ).get(id=hospitalisation_id)
    except Hospitalisation.DoesNotExist:
        raise HttpError(404, 'Hospitalisation introuvable.')
    return _serialize_hospitalisation(h)


@router.get(
    '/patients/{patient_id}/hospitalisation-active/',
    response=HospitalisationOut,
    auth=jwt_auth,
)
def get_hospitalisation_active_patient(request, patient_id: UUID):
    _check_read(request.auth)
    try:
        h = Hospitalisation.objects.select_related(
            'patient',
            'lit__chambre__service__batiment',
        ).get(patient_id=patient_id, statut=StatutHospitalisation.ACTIVE)
    except Hospitalisation.DoesNotExist:
        raise HttpError(404, 'Aucune hospitalisation active pour ce patient.')
    return _serialize_hospitalisation(h)


@router.post('/hospitalisations/{hospitalisation_id}/sortie/', response=HospitalisationOut, auth=jwt_auth)
def enregistrer_sortie(request, hospitalisation_id: UUID, payload: SortieIn):
    _check_sortie(request.auth)
    try:
        hospitalisation = Hospitalisation.objects.select_related(
            'patient',
            'lit__chambre__service__batiment',
        ).get(id=hospitalisation_id)
    except Hospitalisation.DoesNotExist:
        raise HttpError(404, 'Hospitalisation introuvable.')

    try:
        hospitalisation = sortir_patient(
            hospitalisation=hospitalisation,
            hospitalisation_version=payload.version,
        )
    except HospitalisationError as exc:
        _handle_service_error(exc)

    hospitalisation = Hospitalisation.objects.select_related(
        'patient',
        'lit__chambre__service__batiment',
    ).get(id=hospitalisation.id)
    data = _serialize_hospitalisation(hospitalisation)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='Hospitalisation',
        object_id=hospitalisation.id,
        new_value=data.model_dump(),
        ip_address=get_client_ip(request),
    )
    return data

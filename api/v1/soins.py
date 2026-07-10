from datetime import datetime
from typing import Optional
from uuid import UUID

from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from audit.services import get_client_ip, log_audit
from soins.models import ConstanteVitale, DosePlanifiee, InterventionInfirmiere, PlanSoins
from soins.services import (
    SoinsError,
    administrer_dose,
    doses_omises,
    get_hospitalisation_active,
    get_hospitalisation_or_raise,
    get_plan_soins_actif,
    marquer_dose_omise,
)

router = Router(tags=['Soins infirmiers'])
jwt_auth = JWTAuth()

ROLES_LECTURE = {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER, Role.BIOLOGISTE}
ROLES_ECRITURE = {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER}


def _check_read(user: User):
    if user.role not in ROLES_LECTURE:
        raise HttpError(403, 'Accès refusé.')


def _check_write(user: User):
    if user.role not in ROLES_ECRITURE:
        raise HttpError(403, 'Accès refusé.')


def _handle_soins_error(exc: SoinsError):
    status_map = {
        'not_found': 404,
        'version_conflict': 409,
        'hospitalisation_inactive': 400,
        'plan_inactif': 400,
        'dose_deja_traitee': 400,
    }
    raise HttpError(status_map.get(exc.code, 400), exc.message)


class ConstanteVitaleOut(Schema):
    id: UUID
    hospitalisation_id: UUID
    temperature: Optional[float]
    tension_systolique: Optional[int]
    tension_diastolique: Optional[int]
    frequence_cardiaque: Optional[int]
    frequence_respiratoire: Optional[int]
    saturation_o2: Optional[int]
    glycemie: Optional[float]
    mesure_le: datetime
    infirmier_id: Optional[int]
    notes: str


class ConstanteVitaleIn(Schema):
    temperature: Optional[float] = None
    tension_systolique: Optional[int] = None
    tension_diastolique: Optional[int] = None
    frequence_cardiaque: Optional[int] = None
    frequence_respiratoire: Optional[int] = None
    saturation_o2: Optional[int] = None
    glycemie: Optional[float] = None
    mesure_le: Optional[datetime] = None
    notes: str = ''


class PlanSoinsOut(Schema):
    id: UUID
    hospitalisation_id: UUID
    titre: str
    description: str
    date_debut: datetime
    date_fin: Optional[datetime]
    statut: str
    version: int
    cree_par_id: Optional[int]


class PlanSoinsIn(Schema):
    titre: str
    description: str
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None


class InterventionOut(Schema):
    id: UUID
    hospitalisation_id: UUID
    plan_soins_id: Optional[UUID]
    type_intervention: str
    description: str
    realisee_le: datetime
    infirmier_id: Optional[int]


class InterventionIn(Schema):
    type_intervention: str
    description: str
    plan_soins_id: Optional[UUID] = None
    realisee_le: Optional[datetime] = None


class DoseOut(Schema):
    id: UUID
    plan_soins_id: UUID
    medicament: str
    posologie: str
    heure_prevue: datetime
    statut: str
    administree_le: Optional[datetime]
    infirmier_id: Optional[int]
    version: int
    est_en_retard: bool


class DoseIn(Schema):
    medicament: str
    posologie: str
    heure_prevue: datetime


class DoseActionIn(Schema):
    version: int


def _serialize_constante(c: ConstanteVitale) -> ConstanteVitaleOut:
    return ConstanteVitaleOut(
        id=c.id,
        hospitalisation_id=c.hospitalisation_id,
        temperature=float(c.temperature) if c.temperature is not None else None,
        tension_systolique=c.tension_systolique,
        tension_diastolique=c.tension_diastolique,
        frequence_cardiaque=c.frequence_cardiaque,
        frequence_respiratoire=c.frequence_respiratoire,
        saturation_o2=c.saturation_o2,
        glycemie=float(c.glycemie) if c.glycemie is not None else None,
        mesure_le=c.mesure_le,
        infirmier_id=c.infirmier_id,
        notes=c.notes,
    )


def _serialize_plan(p: PlanSoins) -> PlanSoinsOut:
    return PlanSoinsOut(
        id=p.id,
        hospitalisation_id=p.hospitalisation_id,
        titre=p.titre,
        description=p.description,
        date_debut=p.date_debut,
        date_fin=p.date_fin,
        statut=p.statut,
        version=p.version,
        cree_par_id=p.cree_par_id,
    )


def _serialize_intervention(i: InterventionInfirmiere) -> InterventionOut:
    return InterventionOut(
        id=i.id,
        hospitalisation_id=i.hospitalisation_id,
        plan_soins_id=i.plan_soins_id,
        type_intervention=i.type_intervention,
        description=i.description,
        realisee_le=i.realisee_le,
        infirmier_id=i.infirmier_id,
    )


def _serialize_dose(d: DosePlanifiee) -> DoseOut:
    return DoseOut(
        id=d.id,
        plan_soins_id=d.plan_soins_id,
        medicament=d.medicament,
        posologie=d.posologie,
        heure_prevue=d.heure_prevue,
        statut=d.statut,
        administree_le=d.administree_le,
        infirmier_id=d.infirmier_id,
        version=d.version,
        est_en_retard=d.est_en_retard,
    )


@router.get(
    '/hospitalisations/{hospitalisation_id}/constantes-vitales/',
    response=list[ConstanteVitaleOut],
    auth=jwt_auth,
)
@paginate
def list_constantes(request, hospitalisation_id: UUID):
    _check_read(request.auth)
    try:
        get_hospitalisation_or_raise(hospitalisation_id)
    except SoinsError as exc:
        _handle_soins_error(exc)
    qs = ConstanteVitale.objects.filter(hospitalisation_id=hospitalisation_id)
    return [_serialize_constante(c) for c in qs]


@router.post(
    '/hospitalisations/{hospitalisation_id}/constantes-vitales/',
    response=ConstanteVitaleOut,
    auth=jwt_auth,
)
def create_constante(request, hospitalisation_id: UUID, payload: ConstanteVitaleIn):
    _check_write(request.auth)
    try:
        get_hospitalisation_active(hospitalisation_id)
    except SoinsError as exc:
        _handle_soins_error(exc)

    constante = ConstanteVitale(
        hospitalisation_id=hospitalisation_id,
        temperature=payload.temperature,
        tension_systolique=payload.tension_systolique,
        tension_diastolique=payload.tension_diastolique,
        frequence_cardiaque=payload.frequence_cardiaque,
        frequence_respiratoire=payload.frequence_respiratoire,
        saturation_o2=payload.saturation_o2,
        glycemie=payload.glycemie,
        infirmier=request.auth,
        notes=payload.notes,
    )
    if payload.mesure_le is not None:
        constante.mesure_le = payload.mesure_le
    constante.save()
    data = _serialize_constante(constante)
    log_audit(
        user=request.auth,
        action='CREATE',
        model_name='ConstanteVitale',
        object_id=constante.id,
        new_value=data.model_dump(),
        ip_address=get_client_ip(request),
    )
    return data


@router.get(
    '/hospitalisations/{hospitalisation_id}/plans-soins/',
    response=list[PlanSoinsOut],
    auth=jwt_auth,
)
@paginate
def list_plans_soins(request, hospitalisation_id: UUID):
    _check_read(request.auth)
    try:
        get_hospitalisation_or_raise(hospitalisation_id)
    except SoinsError as exc:
        _handle_soins_error(exc)
    qs = PlanSoins.objects.filter(hospitalisation_id=hospitalisation_id)
    return [_serialize_plan(p) for p in qs]


@router.post(
    '/hospitalisations/{hospitalisation_id}/plans-soins/',
    response=PlanSoinsOut,
    auth=jwt_auth,
)
def create_plan_soins(request, hospitalisation_id: UUID, payload: PlanSoinsIn):
    _check_write(request.auth)
    try:
        get_hospitalisation_active(hospitalisation_id)
    except SoinsError as exc:
        _handle_soins_error(exc)

    plan = PlanSoins(
        hospitalisation_id=hospitalisation_id,
        titre=payload.titre,
        description=payload.description,
        cree_par=request.auth,
    )
    if payload.date_debut is not None:
        plan.date_debut = payload.date_debut
    if payload.date_fin is not None:
        plan.date_fin = payload.date_fin
    plan.save()
    data = _serialize_plan(plan)
    log_audit(
        user=request.auth,
        action='CREATE',
        model_name='PlanSoins',
        object_id=plan.id,
        new_value=data.model_dump(),
        ip_address=get_client_ip(request),
    )
    return data


@router.get(
    '/hospitalisations/{hospitalisation_id}/interventions/',
    response=list[InterventionOut],
    auth=jwt_auth,
)
@paginate
def list_interventions(request, hospitalisation_id: UUID):
    _check_read(request.auth)
    try:
        get_hospitalisation_or_raise(hospitalisation_id)
    except SoinsError as exc:
        _handle_soins_error(exc)
    qs = InterventionInfirmiere.objects.filter(hospitalisation_id=hospitalisation_id)
    return [_serialize_intervention(i) for i in qs]


@router.post(
    '/hospitalisations/{hospitalisation_id}/interventions/',
    response=InterventionOut,
    auth=jwt_auth,
)
def create_intervention(request, hospitalisation_id: UUID, payload: InterventionIn):
    _check_write(request.auth)
    try:
        get_hospitalisation_active(hospitalisation_id)
    except SoinsError as exc:
        _handle_soins_error(exc)

    plan = None
    if payload.plan_soins_id:
        try:
            plan = get_plan_soins_actif(payload.plan_soins_id)
            if plan.hospitalisation_id != hospitalisation_id:
                raise HttpError(400, 'Le plan de soins ne correspond pas à cette hospitalisation.')
        except SoinsError as exc:
            _handle_soins_error(exc)

    intervention = InterventionInfirmiere(
        hospitalisation_id=hospitalisation_id,
        plan_soins=plan,
        type_intervention=payload.type_intervention,
        description=payload.description,
        infirmier=request.auth,
    )
    if payload.realisee_le is not None:
        intervention.realisee_le = payload.realisee_le
    intervention.save()
    data = _serialize_intervention(intervention)
    log_audit(
        user=request.auth,
        action='CREATE',
        model_name='InterventionInfirmiere',
        object_id=intervention.id,
        new_value=data.model_dump(),
        ip_address=get_client_ip(request),
    )
    return data


@router.get('/plans-soins/{plan_id}/doses/', response=list[DoseOut], auth=jwt_auth)
@paginate
def list_doses(request, plan_id: UUID):
    _check_read(request.auth)
    try:
        get_plan_soins_actif(plan_id)
    except SoinsError as exc:
        _handle_soins_error(exc)
    qs = DosePlanifiee.objects.filter(plan_soins_id=plan_id)
    return [_serialize_dose(d) for d in qs]


@router.post('/plans-soins/{plan_id}/doses/', response=DoseOut, auth=jwt_auth)
def create_dose(request, plan_id: UUID, payload: DoseIn):
    _check_write(request.auth)
    try:
        get_plan_soins_actif(plan_id)
    except SoinsError as exc:
        _handle_soins_error(exc)

    dose = DosePlanifiee.objects.create(
        plan_soins_id=plan_id,
        medicament=payload.medicament,
        posologie=payload.posologie,
        heure_prevue=payload.heure_prevue,
    )
    data = _serialize_dose(dose)
    log_audit(
        user=request.auth,
        action='CREATE',
        model_name='DosePlanifiee',
        object_id=dose.id,
        new_value=data.model_dump(),
        ip_address=get_client_ip(request),
    )
    return data


@router.post('/doses/{dose_id}/administrer/', response=DoseOut, auth=jwt_auth)
def administrer_dose_endpoint(request, dose_id: UUID, payload: DoseActionIn):
    _check_write(request.auth)
    try:
        dose = DosePlanifiee.objects.get(id=dose_id)
        dose = administrer_dose(dose=dose, infirmier=request.auth, version=payload.version)
    except DosePlanifiee.DoesNotExist:
        raise HttpError(404, 'Dose introuvable.')
    except SoinsError as exc:
        _handle_soins_error(exc)

    data = _serialize_dose(dose)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='DosePlanifiee',
        object_id=dose.id,
        new_value=data.model_dump(),
        ip_address=get_client_ip(request),
    )
    return data


@router.post('/doses/{dose_id}/omission/', response=DoseOut, auth=jwt_auth)
def marquer_omission_dose(request, dose_id: UUID, payload: DoseActionIn):
    _check_write(request.auth)
    try:
        dose = DosePlanifiee.objects.get(id=dose_id)
        dose = marquer_dose_omise(dose=dose, infirmier=request.auth, version=payload.version)
    except DosePlanifiee.DoesNotExist:
        raise HttpError(404, 'Dose introuvable.')
    except SoinsError as exc:
        _handle_soins_error(exc)

    data = _serialize_dose(dose)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='DosePlanifiee',
        object_id=dose.id,
        new_value=data.model_dump(),
        ip_address=get_client_ip(request),
    )
    return data


@router.get('/soins/alertes/doses-omises/', response=list[DoseOut], auth=jwt_auth)
@paginate
def list_doses_omises(request, hospitalisation_id: Optional[UUID] = None):
    _check_read(request.auth)
    qs = doses_omises(hospitalisation_id)
    return [_serialize_dose(d) for d in qs]

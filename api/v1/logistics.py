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
from logistics.models import Batiment, Chambre, Lit, Service, StatutLit
from patients.models import Patient

router = Router(tags=['Logistique'])
jwt_auth = JWTAuth()

ROLES_LECTURE = {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER, Role.BIOLOGISTE}
ROLES_LOGISTIQUE_ECRITURE = {Role.ADMIN}


class BatimentOut(Schema):
    id: UUID
    code: str
    nom: str
    actif: bool


class BatimentIn(Schema):
    code: str
    nom: str
    actif: bool = True


class ServiceOut(Schema):
    id: UUID
    batiment_id: UUID
    batiment_code: str
    code: str
    nom: str
    actif: bool


class ServiceIn(Schema):
    batiment_id: UUID
    code: str
    nom: str
    actif: bool = True


class ChambreOut(Schema):
    id: UUID
    service_id: UUID
    service_code: str
    numero: str
    actif: bool


class ChambreIn(Schema):
    service_id: UUID
    numero: str
    actif: bool = True


class LitOut(Schema):
    id: UUID
    chambre_id: UUID
    chambre_numero: str
    service_code: str
    batiment_code: str
    numero: str
    statut: str
    actif: bool
    version: int
    est_disponible: bool


class LitIn(Schema):
    chambre_id: UUID
    numero: str
    actif: bool = True


class LitStatutIn(Schema):
    statut: str
    version: int


def _check_read(user: User):
    if user.role not in ROLES_LECTURE:
        raise HttpError(403, 'Accès refusé.')


def _check_logistics_write(user: User):
    if user.role not in ROLES_LOGISTIQUE_ECRITURE:
        raise HttpError(403, 'Accès refusé.')


def _serialize_lit(lit: Lit) -> LitOut:
    return LitOut(
        id=lit.id,
        chambre_id=lit.chambre_id,
        chambre_numero=lit.chambre.numero,
        service_code=lit.chambre.service.code,
        batiment_code=lit.chambre.service.batiment.code,
        numero=lit.numero,
        statut=lit.statut,
        actif=lit.actif,
        version=lit.version,
        est_disponible=lit.est_disponible,
    )


@router.get('/logistique/batiments/', response=list[BatimentOut], auth=jwt_auth)
@paginate
def list_batiments(request, actif: Optional[bool] = None):
    _check_read(request.auth)
    qs = Batiment.objects.all()
    if actif is not None:
        qs = qs.filter(actif=actif)
    return [BatimentOut(id=b.id, code=b.code, nom=b.nom, actif=b.actif) for b in qs]


@router.post('/logistique/batiments/', response=BatimentOut, auth=jwt_auth)
def create_batiment(request, payload: BatimentIn):
    _check_logistics_write(request.auth)
    if Batiment.objects.filter(code=payload.code).exists():
        raise HttpError(400, 'Ce code bâtiment existe déjà.')
    batiment = Batiment.objects.create(code=payload.code, nom=payload.nom, actif=payload.actif)
    log_audit(
        user=request.auth,
        action='CREATE',
        model_name='Batiment',
        object_id=batiment.id,
        new_value=payload.model_dump(),
        ip_address=get_client_ip(request),
    )
    return BatimentOut(id=batiment.id, code=batiment.code, nom=batiment.nom, actif=batiment.actif)


@router.get('/logistique/services/', response=list[ServiceOut], auth=jwt_auth)
@paginate
def list_services(request, batiment_id: Optional[UUID] = None):
    _check_read(request.auth)
    qs = Service.objects.select_related('batiment')
    if batiment_id:
        qs = qs.filter(batiment_id=batiment_id)
    return [
        ServiceOut(
            id=s.id,
            batiment_id=s.batiment_id,
            batiment_code=s.batiment.code,
            code=s.code,
            nom=s.nom,
            actif=s.actif,
        )
        for s in qs
    ]


@router.post('/logistique/services/', response=ServiceOut, auth=jwt_auth)
def create_service(request, payload: ServiceIn):
    _check_logistics_write(request.auth)
    try:
        batiment = Batiment.objects.get(id=payload.batiment_id)
    except Batiment.DoesNotExist:
        raise HttpError(404, 'Bâtiment introuvable.')
    if Service.objects.filter(batiment=batiment, code=payload.code).exists():
        raise HttpError(400, 'Ce code service existe déjà pour ce bâtiment.')
    service = Service.objects.create(
        batiment=batiment,
        code=payload.code,
        nom=payload.nom,
        actif=payload.actif,
    )
    return ServiceOut(
        id=service.id,
        batiment_id=service.batiment_id,
        batiment_code=batiment.code,
        code=service.code,
        nom=service.nom,
        actif=service.actif,
    )


@router.get('/logistique/chambres/', response=list[ChambreOut], auth=jwt_auth)
@paginate
def list_chambres(request, service_id: Optional[UUID] = None):
    _check_read(request.auth)
    qs = Chambre.objects.select_related('service')
    if service_id:
        qs = qs.filter(service_id=service_id)
    return [
        ChambreOut(
            id=c.id,
            service_id=c.service_id,
            service_code=c.service.code,
            numero=c.numero,
            actif=c.actif,
        )
        for c in qs
    ]


@router.post('/logistique/chambres/', response=ChambreOut, auth=jwt_auth)
def create_chambre(request, payload: ChambreIn):
    _check_logistics_write(request.auth)
    try:
        service = Service.objects.get(id=payload.service_id)
    except Service.DoesNotExist:
        raise HttpError(404, 'Service introuvable.')
    if Chambre.objects.filter(service=service, numero=payload.numero).exists():
        raise HttpError(400, 'Cette chambre existe déjà pour ce service.')
    chambre = Chambre.objects.create(service=service, numero=payload.numero, actif=payload.actif)
    return ChambreOut(
        id=chambre.id,
        service_id=chambre.service_id,
        service_code=service.code,
        numero=chambre.numero,
        actif=chambre.actif,
    )


@router.get('/logistique/lits/', response=list[LitOut], auth=jwt_auth)
@paginate
def list_lits(request, statut: Optional[str] = None, disponible: Optional[bool] = None):
    _check_read(request.auth)
    qs = Lit.objects.select_related('chambre__service__batiment')
    if statut:
        qs = qs.filter(statut=statut)
    if disponible is True:
        qs = qs.filter(actif=True, statut=StatutLit.LIBRE)
    return [_serialize_lit(lit) for lit in qs]


@router.post('/logistique/lits/', response=LitOut, auth=jwt_auth)
def create_lit(request, payload: LitIn):
    _check_logistics_write(request.auth)
    try:
        chambre = Chambre.objects.get(id=payload.chambre_id)
    except Chambre.DoesNotExist:
        raise HttpError(404, 'Chambre introuvable.')
    if Lit.objects.filter(chambre=chambre, numero=payload.numero).exists():
        raise HttpError(400, 'Ce lit existe déjà dans cette chambre.')
    lit = Lit.objects.create(chambre=chambre, numero=payload.numero, actif=payload.actif)
    return _serialize_lit(lit)


@router.patch('/logistique/lits/{lit_id}/statut/', response=LitOut, auth=jwt_auth)
def update_lit_statut(request, lit_id: UUID, payload: LitStatutIn):
    _check_logistics_write(request.auth)
    if payload.statut not in StatutLit.values:
        raise HttpError(400, 'Statut invalide.')
    try:
        lit = Lit.objects.select_related('chambre__service__batiment').get(id=lit_id)
    except Lit.DoesNotExist:
        raise HttpError(404, 'Lit introuvable.')
    if lit.version != payload.version:
        raise HttpError(409, 'Conflit de version : rechargez le lit et réessayez.')
    if payload.statut == StatutLit.LIBRE and Hospitalisation.objects.filter(
        lit=lit,
        statut=StatutHospitalisation.ACTIVE,
    ).exists():
        raise HttpError(400, 'Impossible de libérer un lit avec une hospitalisation active.')

    old = _serialize_lit(lit).model_dump()
    lit.statut = payload.statut
    lit.bump_version()
    lit.save(update_fields=['statut', 'version', 'updated_at'])
    new = _serialize_lit(lit)
    log_audit(
        user=request.auth,
        action='UPDATE',
        model_name='Lit',
        object_id=lit.id,
        old_value=old,
        new_value=new.model_dump(),
        ip_address=get_client_ip(request),
    )
    return new

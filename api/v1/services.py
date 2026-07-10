from uuid import UUID

from ninja import Router, Schema

from accounts.models import Role
from api.v1.auth_backend import JWTAuth
from api.v1.logistics import ServiceOut
from logistics.models import Batiment, Service

router = Router(tags=['Services médicaux'])
jwt_auth = JWTAuth()

ROLES_LECTURE = {Role.ADMIN, Role.MEDECIN, Role.INFIRMIER, Role.BIOLOGISTE}


class BatimentOut(Schema):
    id: UUID
    code: str
    nom: str
    actif: bool


def _check_read(user):
    if user.role not in ROLES_LECTURE:
        from ninja.errors import HttpError

        raise HttpError(403, 'Accès refusé.')


@router.get('/services/', response=list[ServiceOut], auth=jwt_auth)
def list_services(request, batiment_id: UUID | None = None, actif: bool | None = None):
    _check_read(request.auth)
    qs = Service.objects.select_related('batiment').order_by('batiment__code', 'code')
    if batiment_id:
        qs = qs.filter(batiment_id=batiment_id)
    if actif is not None:
        qs = qs.filter(actif=actif)
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


@router.get('/services/batiments/', response=list[BatimentOut], auth=jwt_auth)
def list_batiments(request, actif: bool | None = None):
    _check_read(request.auth)
    qs = Batiment.objects.all().order_by('code')
    if actif is not None:
        qs = qs.filter(actif=actif)
    return [BatimentOut(id=b.id, code=b.code, nom=b.nom, actif=b.actif) for b in qs]
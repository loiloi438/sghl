from datetime import datetime
from uuid import UUID

from django.db.models import Q
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate

from accounts.models import User
from api.v1.auth_backend import JWTAuth
from notifications.models import DeviceToken, NotificationInbox, PlateformeAppareil
from notifications.push_service import enregistrer_appareil, marquer_lu

router = Router(tags=['Notifications'])
jwt_auth = JWTAuth()


class NotificationOut(Schema):
    id: UUID
    titre: str
    corps: str
    categorie: str
    donnees: dict
    lu: bool
    created_at: datetime


class NotificationCountOut(Schema):
    count: int


class AppareilIn(Schema):
    token: str
    plateforme: str = PlateformeAppareil.INCONNU


def _notification_q(search: str | None):
    if not search:
        return Q()
    return (
        Q(titre__icontains=search)
        | Q(corps__icontains=search)
        | Q(categorie__icontains=search)
        | Q(donnees__icontains=search)
    )


@router.get('/notifications/', response=list[NotificationOut], auth=jwt_auth)
@paginate
def list_notifications(request, search: str | None = None, lu: bool | None = None):
    user: User = request.auth
    qs = NotificationInbox.objects.filter(utilisateur=user).order_by('-created_at')
    qs = qs.filter(_notification_q(search))
    if lu is not None:
        qs = qs.filter(lu=lu)
    return qs


@router.get('/notifications/non-lues/', response=NotificationCountOut, auth=jwt_auth)
def count_notifications_non_lues(request):
    user: User = request.auth
    return NotificationCountOut(count=NotificationInbox.objects.filter(utilisateur=user, lu=False).count())


@router.post('/notifications/{notification_id}/lu/', auth=jwt_auth)
def mark_notification_read(request, notification_id: UUID):
    user: User = request.auth
    if not marquer_lu(notification_id, user.id):
        raise HttpError(404, 'Notification introuvable.')
    return {'detail': 'Notification lue.'}


@router.post('/notifications/appareils/', auth=jwt_auth)
def register_device(request, payload: AppareilIn):
    user: User = request.auth
    try:
        enregistrer_appareil(
            utilisateur_id=user.id,
            token=payload.token,
            plateforme=payload.plateforme,
        )
    except ValueError as exc:
        raise HttpError(400, str(exc))
    return {'detail': 'Appareil enregistré.'}


@router.post('/notifications/appareils/desactiver/', auth=jwt_auth)
def deactivate_device(request, payload: AppareilIn):
    user: User = request.auth
    DeviceToken.objects.filter(utilisateur_id=user.id, token=payload.token.strip()).update(actif=False)
    return {'detail': 'Appareil désactivé.'}
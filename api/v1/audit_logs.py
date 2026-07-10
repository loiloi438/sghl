from datetime import datetime
from typing import Optional

from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from audit.models import AuditLog

router = Router(tags=['Audit'])
jwt_auth = JWTAuth()


class AuditLogOut(Schema):
    id: int
    utilisateur: Optional[str]
    action: str
    model_name: str
    object_id: str
    ip_address: Optional[str]
    timestamp: datetime


def _require_admin(user: User):
    if user.role != Role.ADMIN:
        raise HttpError(403, 'Réservé aux administrateurs.')


@router.get('/audit/logs/', response=list[AuditLogOut], auth=jwt_auth)
@paginate
def lister_audit(request, model_name: str = '', action: str = ''):
    _require_admin(request.auth)
    qs = AuditLog.objects.select_related('user').order_by('-timestamp')
    if model_name:
        qs = qs.filter(model_name__icontains=model_name)
    if action:
        qs = qs.filter(action=action.upper())
    return [
        AuditLogOut(
            id=log.id,
            utilisateur=(
                f'{log.user.first_name} {log.user.last_name}'.strip() or log.user.username
                if log.user
                else None
            ),
            action=log.action,
            model_name=log.model_name,
            object_id=log.object_id,
            ip_address=str(log.ip_address) if log.ip_address else None,
            timestamp=log.timestamp,
        )
        for log in qs
    ]

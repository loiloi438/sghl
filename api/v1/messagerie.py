from datetime import datetime
from uuid import UUID

from django.db.models import Q
from django.utils import timezone
from ninja import Router, Schema
from ninja.errors import HttpError

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from messagerie.models import MessageInterne

router = Router(tags=['Messagerie'])
jwt_auth = JWTAuth()

STAFF_MESSAGERIE = {
    Role.ADMIN,
    Role.MEDECIN,
    Role.INFIRMIER,
    Role.COMPTABLE,
    Role.SECRETAIRE,
}


class MessageOut(Schema):
    id: UUID
    sujet: str
    corps: str
    lu: bool
    created_at: datetime
    expediteur_nom: str
    expediteur_role: str
    destinataire_nom: str
    destinataire_role: str
    sens: str


class MessageIn(Schema):
    destinataire_id: int | None = None
    sujet: str
    corps: str


class StaffOptionOut(Schema):
    id: int
    full_name: str
    role: str
    role_label: str


def _user_label(user: User) -> str:
    return f'{user.first_name} {user.last_name}'.strip() or user.username


def _serialize(msg: MessageInterne, viewer: User) -> MessageOut:
    sens = 'recu' if msg.destinataire_id == viewer.id else 'envoye'
    return MessageOut(
        id=msg.id,
        sujet=msg.sujet,
        corps=msg.corps,
        lu=msg.lu,
        created_at=msg.created_at,
        expediteur_nom=_user_label(msg.expediteur),
        expediteur_role=msg.expediteur.role,
        destinataire_nom=_user_label(msg.destinataire),
        destinataire_role=msg.destinataire.role,
        sens=sens,
    )


def _default_secretariat() -> User:
    user = User.objects.filter(role=Role.SECRETAIRE, is_active=True).order_by('id').first()
    if user is None:
        user = User.objects.filter(role=Role.COMPTABLE, is_active=True).order_by('id').first()
    if user is None:
        user = User.objects.filter(role=Role.ADMIN, is_active=True).order_by('id').first()
    if user is None:
        raise HttpError(503, 'Aucun destinataire secrétariat disponible.')
    return user


@router.get('/messagerie/', response=list[MessageOut], auth=jwt_auth)
def list_messages_staff(request, lu: bool | None = None):
    user = request.auth
    if user.role not in STAFF_MESSAGERIE:
        raise HttpError(403, 'Accès refusé.')
    qs = MessageInterne.objects.filter(
        Q(destinataire=user) | Q(expediteur=user),
    ).select_related('expediteur', 'destinataire')
    if lu is not None:
        qs = qs.filter(destinataire=user, lu=lu)
    return [_serialize(m, user) for m in qs[:100]]


@router.get('/messagerie/contacts/', response=list[StaffOptionOut], auth=jwt_auth)
def list_contacts_staff(request):
    user = request.auth
    if user.role not in STAFF_MESSAGERIE and user.role != Role.PATIENT:
        raise HttpError(403, 'Accès refusé.')
    if user.role == Role.PATIENT:
        qs = User.objects.filter(role__in=STAFF_MESSAGERIE, is_active=True)
    else:
        qs = User.objects.filter(is_active=True).exclude(id=user.id)
    return [
        StaffOptionOut(
            id=u.id,
            full_name=_user_label(u),
            role=u.role,
            role_label=u.get_role_display(),
        )
        for u in qs.order_by('last_name', 'first_name')[:50]
    ]


@router.post('/messagerie/', response=MessageOut, auth=jwt_auth)
def send_message_staff(request, payload: MessageIn):
    user = request.auth
    if user.role not in STAFF_MESSAGERIE and user.role != Role.PATIENT:
        raise HttpError(403, 'Accès refusé.')
    sujet = payload.sujet.strip()
    corps = payload.corps.strip()
    if not sujet or not corps:
        raise HttpError(400, 'Sujet et message obligatoires.')
    if user.role == Role.PATIENT:
        destinataire = _default_secretariat()
    else:
        if not payload.destinataire_id:
            raise HttpError(400, 'Destinataire obligatoire.')
        try:
            destinataire = User.objects.get(pk=payload.destinataire_id, is_active=True)
        except User.DoesNotExist as exc:
            raise HttpError(404, 'Destinataire introuvable.') from exc
    msg = MessageInterne.objects.create(
        expediteur=user,
        destinataire=destinataire,
        sujet=sujet,
        corps=corps,
    )
    return _serialize(msg, user)


@router.post('/messagerie/{message_id}/lu/', auth=jwt_auth)
def mark_read_staff(request, message_id: UUID):
    user = request.auth
    try:
        msg = MessageInterne.objects.get(pk=message_id, destinataire=user)
    except MessageInterne.DoesNotExist as exc:
        raise HttpError(404, 'Message introuvable.') from exc
    if not msg.lu:
        msg.lu = True
        msg.lu_le = timezone.now()
        msg.save(update_fields=['lu', 'lu_le'])
    return {'detail': 'Message marqué comme lu.'}


@router.get('/patient/messages/', response=list[MessageOut], auth=jwt_auth)
def list_messages_patient(request):
    user = request.auth
    if user.role != Role.PATIENT:
        raise HttpError(403, 'Accès réservé aux patients.')
    qs = MessageInterne.objects.filter(
        Q(destinataire=user) | Q(expediteur=user),
    ).select_related('expediteur', 'destinataire')
    return [_serialize(m, user) for m in qs[:100]]


@router.post('/patient/messages/', response=MessageOut, auth=jwt_auth)
def send_message_patient(request, payload: MessageIn):
    user = request.auth
    if user.role != Role.PATIENT:
        raise HttpError(403, 'Accès réservé aux patients.')
    sujet = payload.sujet.strip()
    corps = payload.corps.strip()
    if not sujet or not corps:
        raise HttpError(400, 'Sujet et message obligatoires.')
    destinataire = _default_secretariat()
    if payload.destinataire_id:
        try:
            destinataire = User.objects.get(
                pk=payload.destinataire_id,
                role__in=STAFF_MESSAGERIE,
                is_active=True,
            )
        except User.DoesNotExist as exc:
            raise HttpError(404, 'Destinataire introuvable.') from exc
    msg = MessageInterne.objects.create(
        expediteur=user,
        destinataire=destinataire,
        sujet=sujet,
        corps=corps,
    )
    return _serialize(msg, user)


@router.post('/patient/messages/{message_id}/lu/', auth=jwt_auth)
def mark_read_patient(request, message_id: UUID):
    user = request.auth
    if user.role != Role.PATIENT:
        raise HttpError(403, 'Accès réservé aux patients.')
    try:
        msg = MessageInterne.objects.get(pk=message_id, destinataire=user)
    except MessageInterne.DoesNotExist as exc:
        raise HttpError(404, 'Message introuvable.') from exc
    if not msg.lu:
        msg.lu = True
        msg.lu_le = timezone.now()
        msg.save(update_fields=['lu', 'lu_le'])
    return {'detail': 'Message marqué comme lu.'}

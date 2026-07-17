from typing import Optional

from django.conf import settings
from ninja import Router, Schema
from ninja.errors import HttpError

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from audit.services import get_client_ip, log_audit
from core.models import ConfigurationEtablissement

router = Router(tags=['Paramètres'])
jwt_auth = JWTAuth()


def _contact_email(cfg: ConfigurationEtablissement) -> str:
    for candidate in (
        getattr(settings, 'SGHL_ADMIN_EMAIL', ''),
        getattr(settings, 'SGHL_SUPPORT_EMAIL', ''),
        cfg.email,
    ):
        email = (candidate or '').strip()
        if email and email != 'support@sghl.local':
            return email
    return (cfg.email or '').strip() or getattr(settings, 'SGHL_SUPPORT_EMAIL', 'support@sghl.local')


class ParametresPublicOut(Schema):
    organization_name: str
    address: str
    phone: str
    email: str
    latitude: float
    longitude: float


class ParametresOut(Schema):
    organization_name: str
    address: str
    phone: str
    email: str
    finess_number: str
    mfa_required: bool
    session_timeout_minutes: int
    max_login_attempts: int
    audit_logging_enabled: bool
    encryption_level: str
    maintenance_mode: bool
    maintenance_message: str
    hl7_enabled: bool
    fhir_enabled: bool
    insurance_api_enabled: bool
    version: int


class ParametresIn(Schema):
    version: int
    organization_name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    finess_number: Optional[str] = None
    mfa_required: Optional[bool] = None
    session_timeout_minutes: Optional[int] = None
    max_login_attempts: Optional[int] = None
    audit_logging_enabled: Optional[bool] = None
    encryption_level: Optional[str] = None
    maintenance_mode: Optional[bool] = None
    maintenance_message: Optional[str] = None
    hl7_enabled: Optional[bool] = None
    fhir_enabled: Optional[bool] = None
    insurance_api_enabled: Optional[bool] = None


def _check_admin(user: User):
    if user.role != Role.ADMIN:
        raise HttpError(403, 'Accès réservé à l’administrateur.')


def _serialize(cfg: ConfigurationEtablissement) -> ParametresOut:
    return ParametresOut(
        organization_name=cfg.organization_name,
        address=cfg.address,
        phone=cfg.phone,
        email=cfg.email,
        finess_number=cfg.finess_number,
        mfa_required=cfg.mfa_required,
        session_timeout_minutes=cfg.session_timeout_minutes,
        max_login_attempts=cfg.max_login_attempts,
        audit_logging_enabled=cfg.audit_logging_enabled,
        encryption_level=cfg.encryption_level,
        maintenance_mode=cfg.maintenance_mode,
        maintenance_message=cfg.maintenance_message,
        hl7_enabled=cfg.hl7_enabled,
        fhir_enabled=cfg.fhir_enabled,
        insurance_api_enabled=cfg.insurance_api_enabled,
        version=cfg.version,
    )


@router.get('/parametres/public/', response=ParametresPublicOut)
def get_parametres_public(request):
    cfg = ConfigurationEtablissement.get_solo()
    return ParametresPublicOut(
        organization_name=cfg.organization_name,
        address=cfg.address,
        phone=cfg.phone,
        email=_contact_email(cfg),
        latitude=getattr(settings, 'SGHL_LATITUDE', -4.2839),
        longitude=getattr(settings, 'SGHL_LONGITUDE', 12.9860),
    )


class ContactPublicIn(Schema):
    nom: str
    email: str
    message: str


@router.post('/contact/')
def contact_public(request, payload: ContactPublicIn):
    """Formulaire de contact public (mode observateur)."""
    nom = (payload.nom or '').strip()
    email = (payload.email or '').strip()
    message = (payload.message or '').strip()
    if len(nom) < 2:
        raise HttpError(400, 'Indiquez votre nom.')
    if '@' not in email or len(email) < 5:
        raise HttpError(400, 'Adresse e-mail invalide.')
    if len(message) < 10:
        raise HttpError(400, 'Votre message est trop court.')
    if len(message) > 2000:
        raise HttpError(400, 'Votre message est trop long.')

    dest = _contact_email(ConfigurationEtablissement.get_solo())
    subject = f'[SGHL Contact] Message de {nom}'
    body = f'De : {nom} <{email}>\n\n{message}\n'
    try:
        from django.core.mail import send_mail

        send_mail(
            subject=subject,
            message=body,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            recipient_list=[dest],
            fail_silently=True,
        )
    except Exception:
        pass
    return {'ok': True, 'detail': 'Message reçu.'}


@router.get('/parametres/', response=ParametresOut, auth=jwt_auth)
def get_parametres(request):
    _check_admin(request.auth)
    return _serialize(ConfigurationEtablissement.get_solo())


@router.patch('/parametres/', response=ParametresOut, auth=jwt_auth)
def update_parametres(request, payload: ParametresIn):
    _check_admin(request.auth)
    cfg = ConfigurationEtablissement.get_solo()
    if cfg.version != payload.version:
        raise HttpError(409, 'Conflit de version.')
    old = _serialize(cfg).dict()
    fields = payload.dict(exclude={'version'}, exclude_none=True)
    for key, value in fields.items():
        setattr(cfg, key, value)
    cfg.bump_version()
    cfg.save()
    log_audit(
        user=request.auth,
        action='update',
        model_name='ConfigurationEtablissement',
        object_id='1',
        old_value=old,
        new_value=_serialize(cfg).dict(),
        ip_address=get_client_ip(request),
    )
    return _serialize(cfg)

from datetime import date
from typing import Optional

from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from ninja import Router, Schema
from ninja.errors import HttpError

from accounts.emails import notifier_mfa_active, notifier_mfa_code
from accounts.jwt_service import (
    create_access_token,
    create_refresh_token,
    login_user,
    revoke_refresh_token,
    rotate_refresh_token,
)
from accounts.mfa_service import generate_secret, provisioning_uri, verify_totp
from core.email_utils import is_otp_production
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password, check_password
from accounts.models import AccountValidation
from accounts.models import Role, User
from accounts.password_reset_service import demander_reinitialisation_mdp, reinitialiser_mot_de_passe
from accounts.rate_limit import clear_login_failures, is_login_blocked, record_login_failure
from accounts.registration_service import (
    InscriptionPatientError,
    inscrire_patient,
    verifier_code_validation,
    renvoyer_code_validation,
)
from api.v1.auth_backend import JWTAuth
from audit.services import get_client_ip, log_audit

router = Router(tags=['Authentification'])
jwt_auth = JWTAuth()


class LoginIn(Schema):
    username: str
    password: str
    totp_code: Optional[str] = None


class MfaSetupOut(Schema):
    secret: str
    provisioning_uri: str
    detail: str


class MfaCodeIn(Schema):
    code: str


class TokenOut(Schema):
    access_token: str
    refresh_token: str
    token_type: str = 'Bearer'


class RefreshIn(Schema):
    refresh_token: str


class UserOut(Schema):
    id: int
    username: str
    email: str
    role: str
    first_name: str
    last_name: str
    mfa_enabled: bool


class MessageOut(Schema):
    detail: str


class PatientRegisterIn(Schema):
    nom: str
    prenom: str
    date_naissance: date
    sexe: str
    email: str = ''
    telephone: str = ''
    password: str
    password_confirm: str
    consentement_rgpd: bool = False


class PatientRegisterOut(Schema):
    username: str
    detail: str
    dev_validation_code: Optional[str] = None


class PasswordForgotIn(Schema):
    identifiant: str


class PasswordResetIn(Schema):
    uid: str
    token: str
    new_password: str
    new_password_confirm: str


@router.post('/auth/login/', response=TokenOut)
def login(request, payload: LoginIn):
    ip = get_client_ip(request)
    if is_login_blocked(ip, payload.username):
        raise HttpError(429, 'Trop de tentatives. Réessayez dans quelques minutes.')
    try:
        pending_user = User.objects.get(username=payload.username)
        if pending_user.check_password(payload.password) and not pending_user.is_active:
            record_login_failure(ip, payload.username)
            raise HttpError(
                403,
                'Compte non activé. Saisissez le code reçu par e-mail pour valider votre inscription.',
            )
    except User.DoesNotExist:
        pass
    result = login_user(payload.username, payload.password)
    if result is None:
        record_login_failure(ip, payload.username)
        raise HttpError(401, 'Identifiants invalides.')
    user, access, refresh = result
    if user.role != Role.PATIENT and not user.mfa_enabled:
        record_login_failure(ip, payload.username)
        raise HttpError(403, 'MFA obligatoire pour le personnel. Activez MFA avant de vous connecter.')
    # If user has MFA enabled, support two-step MFA by email/SMS.
    if user.mfa_enabled:
        # if a TOTP code is provided (legacy TOTP flow), verify it
        if payload.totp_code:
            if not verify_totp(user.mfa_secret, payload.totp_code):
                record_login_failure(ip, payload.username)
                raise HttpError(401, 'Code MFA requis ou invalide.')
        else:
            # generate a one-time numeric code, store hashed, send by email/SMS and
            # inform client that MFA step is required (202)
            code = get_random_string(length=6, allowed_chars='0123456789')
            hash_ = make_password(code)
            AccountValidation.objects.create(user=user, code_hash=hash_)
            # send code via email (or SMS resolver in notifier)
            sent = notifier_mfa_code(user.id, code)
            if not sent and is_otp_production():
                raise HttpError(500, 'Impossible d\'envoyer le code MFA. Contactez l\'administrateur.')
            raise HttpError(202, 'MFA_REQUIRED')
    # Non-patient users without MFA enabled receive a warning but are allowed to login (they should enable MFA)
    clear_login_failures(ip, payload.username)
    log_audit(
        user=user,
        action='CREATE',
        model_name='Session',
        object_id=user.id,
        new_value={'event': 'login'},
        ip_address=get_client_ip(request),
    )
    return TokenOut(access_token=access, refresh_token=refresh)


class MfaLoginIn(Schema):
    username: str
    code: str


@router.post('/auth/login/mfa/', response=TokenOut)
def login_mfa(request, payload: MfaLoginIn):
    """Second step MFA: verify temporary code sent by email/SMS and return tokens."""
    ip = get_client_ip(request)
    try:
        user = User.objects.get(username=payload.username)
    except User.DoesNotExist:
        raise HttpError(404, 'Utilisateur introuvable.')

    # find latest non-used validation
    validation = (
        AccountValidation.objects.filter(user=user, used=False).order_by('-created_at').first()
    )
    if not validation:
        raise HttpError(400, 'Aucun code MFA trouvé. Demandez un nouveau code.')

    # expiry (5 minutes)
    from django.utils import timezone
    from datetime import timedelta
    if timezone.now() > validation.created_at + timedelta(minutes=5):
        raise HttpError(400, 'Le code a expiré. Demandez un nouveau code.')

    if not check_password(payload.code, validation.code_hash):
        validation.attempts += 1
        validation.save(update_fields=['attempts'])
        raise HttpError(401, 'Code MFA invalide.')

    # Mark used and return tokens
    validation.used = True
    validation.save(update_fields=['used'])

    # create tokens directly (bypass password since validated)
    from accounts.jwt_service import create_access_token, create_refresh_token

    if not user.is_active:
        raise HttpError(403, 'Compte inactif.')

    access = create_access_token(user)
    refresh = create_refresh_token(user)
    clear_login_failures(ip, payload.username)
    log_audit(
        user=user,
        action='CREATE',
        model_name='Session',
        object_id=user.id,
        new_value={'event': 'login_mfa'},
        ip_address=get_client_ip(request),
    )
    return TokenOut(access_token=access, refresh_token=refresh)


@router.post('/auth/refresh/', response=TokenOut)
def refresh_token(request, payload: RefreshIn):
    result = rotate_refresh_token(payload.refresh_token)
    if result is None:
        raise HttpError(401, 'Jeton de rafraîchissement invalide ou expiré.')
    access, refresh = result
    return TokenOut(access_token=access, refresh_token=refresh)


@router.post('/auth/logout/')
def logout(request, payload: RefreshIn):
    revoke_refresh_token(payload.refresh_token)
    return {'detail': 'Déconnexion effectuée.'}


@router.post('/auth/mfa/setup/', response=MfaSetupOut, auth=jwt_auth)
def mfa_setup(request):
    user: User = request.auth
    secret = generate_secret()
    user.mfa_secret = secret
    user.mfa_enabled = False
    user.save(update_fields=['mfa_secret', 'mfa_enabled'])
    uri = provisioning_uri(username=user.username, secret=secret)
    return MfaSetupOut(
        secret=secret,
        provisioning_uri=uri,
        detail='Scannez l’URI dans Google Authenticator puis appelez /auth/mfa/enable/.',
    )


@router.post('/auth/mfa/enable/', auth=jwt_auth)
def mfa_enable(request, payload: MfaCodeIn):
    user: User = request.auth
    if not user.mfa_secret:
        raise HttpError(400, 'Appelez d’abord /auth/mfa/setup/.')
    if not verify_totp(user.mfa_secret, payload.code):
        raise HttpError(400, 'Code MFA invalide.')
    user.mfa_enabled = True
    user.save(update_fields=['mfa_enabled'])
    user_id = user.id
    transaction.on_commit(lambda: notifier_mfa_active(user_id))
    return {'detail': 'MFA activé.'}


@router.get('/auth/me/', response=UserOut, auth=jwt_auth)
def me(request):
    user: User = request.auth
    return UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
        mfa_enabled=user.mfa_enabled,
    )


@router.post('/auth/register/patient/', response=PatientRegisterOut)
def register_patient(request, payload: PatientRegisterIn):
    try:
        user, validation_code = inscrire_patient(
            nom=payload.nom,
            prenom=payload.prenom,
            date_naissance=payload.date_naissance,
            sexe=payload.sexe,
            email=payload.email,
            telephone=payload.telephone,
            password=payload.password,
            password_confirm=payload.password_confirm,
            consentement_rgpd=payload.consentement_rgpd,
        )
    except InscriptionPatientError as exc:
        raise HttpError(exc.status, exc.message) from exc

    log_audit(
        user=user,
        action='CREATE',
        model_name='User',
        object_id=user.id,
        new_value={'event': 'patient_self_register'},
        ip_address=get_client_ip(request),
    )
    return PatientRegisterOut(
        username=user.username,
        detail=(
            'Compte patient créé. Un e-mail de confirmation vous a été envoyé si applicable. '
            'Veuillez saisir le code reçu pour activer votre compte.'
        ),
        dev_validation_code=validation_code if settings.DEBUG else None,
    )


class ValidateAccountIn(Schema):
    username: str
    code: str


class ValidateAccountOut(Schema):
    detail: str
    access_token: str
    refresh_token: str
    token_type: str = 'Bearer'


@router.post('/auth/validate/', response=ValidateAccountOut)
def validate_account(request, payload: ValidateAccountIn):
    try:
        user = verifier_code_validation(username=payload.username, code=payload.code)
    except InscriptionPatientError as exc:
        raise HttpError(exc.status, exc.message) from exc

    ip = get_client_ip(request)
    clear_login_failures(ip, payload.username)
    access = create_access_token(user)
    refresh = create_refresh_token(user)
    log_audit(
        user=user,
        action='UPDATE',
        model_name='User',
        object_id=user.id,
        new_value={'event': 'account_validated'},
        ip_address=ip,
    )
    return ValidateAccountOut(
        detail='Compte activé. Bienvenue dans votre espace patient.',
        access_token=access,
        refresh_token=refresh,
    )


class ResendValidationIn(Schema):
    username: str


@router.post('/auth/validate/resend/', response=MessageOut)
def resend_validation(request, payload: ResendValidationIn):
    try:
        renvoyer_code_validation(username=payload.username)
    except InscriptionPatientError as exc:
        raise HttpError(exc.status, exc.message) from exc
    return MessageOut(detail='Un nouveau code de validation a été envoyé si votre e-mail est renseigné.')


@router.post('/auth/password/forgot/', response=MessageOut)
def password_forgot(request, payload: PasswordForgotIn):
    demander_reinitialisation_mdp(identifiant=payload.identifiant)
    return MessageOut(
        detail=(
            'Si un compte correspond à cet identifiant, un lien de réinitialisation '
            'a été envoyé par e-mail ou SMS.'
        ),
    )


@router.post('/auth/password/reset/', response=MessageOut)
def password_reset(request, payload: PasswordResetIn):
    if payload.new_password != payload.new_password_confirm:
        raise HttpError(400, 'Les mots de passe ne correspondent pas.')
    try:
        validate_password(payload.new_password)
    except ValidationError as exc:
        raise HttpError(400, ' '.join(exc.messages)) from exc
    try:
        user = reinitialiser_mot_de_passe(
            uid=payload.uid,
            token=payload.token,
            new_password=payload.new_password,
        )
    except ValueError as exc:
        raise HttpError(400, str(exc)) from exc

    log_audit(
        user=user,
        action='UPDATE',
        model_name='User',
        object_id=user.id,
        new_value={'event': 'password_reset'},
        ip_address=get_client_ip(request),
    )
    return MessageOut(detail='Mot de passe mis à jour. Vous pouvez vous connecter.')

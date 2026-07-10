import logging

from django.conf import settings

from accounts.models import User
from core.email_utils import (
    envoyer_email_template,
    is_otp_production,
    notifications_actives,
    resoudre_email_patient,
    resoudre_email_utilisateur,
)

logger = logging.getLogger(__name__)


def _log_otp_code(user: User, code: str, purpose: str) -> None:
    logger.info('OTP %s pour %s : %s', purpose, user.username, code)


def notifier_mfa_active(user_id: int) -> bool:
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning('E-mail MFA ignoré : utilisateur %s introuvable.', user_id)
        return False

    destinataire = resoudre_email_utilisateur(user)
    if not destinataire:
        logger.info('Pas d\'e-mail pour notification MFA (user %s).', user_id)
        return False

    nom = f'{user.first_name} {user.last_name}'.strip() or user.username
    return envoyer_email_template(
        destinataire=destinataire,
        sujet=f'[{settings.SGHL_ETABLISSEMENT}] Authentification à deux facteurs activée',
        template_base='accounts/emails/mfa_active',
        contexte={
            'utilisateur_nom': nom,
            'username': user.username,
            'role': user.get_role_display(),
        },
    )


def notifier_inscription_patient(user_id: int, patient_id) -> bool:
    from patients.models import Patient

    try:
        user = User.objects.get(pk=user_id)
        patient = Patient.objects.get(pk=patient_id)
    except (User.DoesNotExist, Patient.DoesNotExist):
        return False

    destinataire = resoudre_email_utilisateur(user) or resoudre_email_patient(patient)
    if not destinataire:
        logger.info('Pas d\'e-mail pour confirmation inscription (user %s).', user_id)
        return False

    nom = f'{patient.prenom} {patient.nom}'.strip()
    return envoyer_email_template(
        destinataire=destinataire,
        sujet=f'[{settings.SGHL_ETABLISSEMENT}] Bienvenue — votre espace patient',
        template_base='accounts/emails/inscription_patient',
        contexte={
            'patient_nom': nom,
            'username': user.username,
            'numero_dossier': patient.numero_dossier,
        },
    )


def notifier_reinitialisation_mdp(user_id: int, lien: str) -> bool:
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return False

    destinataire = resoudre_email_utilisateur(user)
    if not destinataire:
        logger.info('Pas d\'e-mail pour réinitialisation MDP (user %s).', user_id)
        return False

    nom = f'{user.first_name} {user.last_name}'.strip() or user.username
    return envoyer_email_template(
        destinataire=destinataire,
        sujet=f'[{settings.SGHL_ETABLISSEMENT}] Réinitialisation de mot de passe',
        template_base='accounts/emails/password_reset',
        contexte={
            'utilisateur_nom': nom,
            'username': user.username,
            'lien_reinitialisation': lien,
        },
    )


def notifier_validation_code(user_id: int, patient_id: int, code: str) -> bool:
    from patients.models import Patient

    try:
        user = User.objects.get(pk=user_id)
        patient = Patient.objects.get(pk=patient_id)
    except (User.DoesNotExist, Patient.DoesNotExist):
        return False

    destinataire = resoudre_email_utilisateur(user) or resoudre_email_patient(patient)
    if not destinataire:
        if not is_otp_production():
            _log_otp_code(user, code, 'validation de compte (sans e-mail)')
            return True
        logger.info('Pas d\'e-mail pour validation inscription (user %s).', user_id)
        return False

    if not notifications_actives():
        if not is_otp_production():
            _log_otp_code(user, code, 'validation de compte (e-mail désactivé)')
            return True
        return False

    if not is_otp_production():
        _log_otp_code(user, code, 'validation de compte')

    nom = f'{patient.prenom} {patient.nom}'.strip()
    return envoyer_email_template(
        destinataire=destinataire,
        sujet=f'Validation de votre compte SGHL',
        template_base='accounts/emails/validation_code',
        contexte={
            'patient_nom': nom,
            'code_validation': code,
        },
    )


def notifier_validation_code_user(user_id: int, code: str) -> bool:
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return False

    destinataire = resoudre_email_utilisateur(user)
    if not destinataire:
        if not is_otp_production():
            _log_otp_code(user, code, 'validation de compte staff (sans e-mail)')
            return True
        logger.info('Pas d\'e-mail pour validation inscription staff (user %s).', user_id)
        return False

    if not notifications_actives():
        if not is_otp_production():
            _log_otp_code(user, code, 'validation de compte staff (e-mail désactivé)')
            return True
        return False

    if not is_otp_production():
        _log_otp_code(user, code, 'validation de compte staff')

    nom = f'{user.first_name} {user.last_name}'.strip() or user.username
    return envoyer_email_template(
        destinataire=destinataire,
        sujet=f'Validation de votre compte SGHL',
        template_base='accounts/emails/validation_code',
        contexte={
            'patient_nom': nom,
            'code_validation': code,
        },
    )


def notifier_mfa_code(user_id: int, code: str) -> bool:
    """Envoie un code MFA temporaire (OTP) à l'utilisateur par e-mail.
    Utilisé pour la seconde étape d'authentification (code par e-mail/SMS).
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning('E-mail MFA code ignoré : utilisateur %s introuvable.', user_id)
        return False

    destinataire = resoudre_email_utilisateur(user)
    if not destinataire:
        if not is_otp_production():
            _log_otp_code(user, code, 'MFA (sans e-mail)')
            return True
        logger.info('Pas d\'e-mail pour envoi du code MFA (user %s).', user_id)
        return False

    if not notifications_actives():
        if not is_otp_production():
            _log_otp_code(user, code, 'MFA (e-mail désactivé)')
            return True
        return False

    if not is_otp_production():
        _log_otp_code(user, code, 'MFA')

    nom = f'{user.first_name} {user.last_name}'.strip() or user.username
    return envoyer_email_template(
        destinataire=destinataire,
        sujet=f'[{settings.SGHL_ETABLISSEMENT}] Code de connexion',
        template_base='accounts/emails/mfa_code',
        contexte={
            'utilisateur_nom': nom,
            'code_mfa': code,
            'expire_minutes': 5,
        },
    )

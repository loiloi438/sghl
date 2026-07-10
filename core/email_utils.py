import logging
from typing import Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from patients.models import Patient

logger = logging.getLogger(__name__)


def notifications_actives() -> bool:
    return getattr(settings, 'EMAIL_NOTIFICATIONS_ENABLED', True)


def otp_mode() -> str:
    mode = getattr(settings, 'OTP_MODE', None)
    if mode is not None:
        return str(mode).strip().lower()
    return 'development' if settings.DEBUG else 'production'


def is_otp_production() -> bool:
    return otp_mode() == 'production'


def resoudre_email_patient(patient: Patient) -> Optional[str]:
    email = (patient.email or '').strip()
    if email:
        return email
    compte = patient.compte_utilisateur
    if compte and compte.email:
        return compte.email.strip()
    return None


def resoudre_email_utilisateur(user) -> Optional[str]:
    email = (user.email or '').strip()
    return email or None


def envoyer_email_template(
    *,
    destinataire: str,
    sujet: str,
    template_base: str,
    contexte: dict,
) -> bool:
    if not notifications_actives():
        return False

    contexte = {**contexte, 'etablissement': settings.SGHL_ETABLISSEMENT}
    texte = render_to_string(f'{template_base}.txt', contexte)
    html = render_to_string(f'{template_base}.html', contexte)

    message = EmailMultiAlternatives(
        subject=sujet,
        body=texte,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[destinataire],
    )
    message.attach_alternative(html, 'text/html')
    try:
        message.send(fail_silently=False)
        return True
    except Exception:
        logger.exception('Échec envoi e-mail à %s (%s)', destinataire, template_base)
        return False

"""Backend e-mail Brevo (HTTP/443) — contourne le blocage SMTP du plan Render gratuit."""

import logging

import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class BrevoEmailBackend(BaseEmailBackend):
    """Envoie les e-mails via l'API REST Brevo (port 443, autorisé sur Render free)."""

    def send_messages(self, email_messages):
        api_key = (getattr(settings, 'BREVO_API_KEY', '') or '').strip()
        if not api_key:
            logger.error('BREVO_API_KEY non configuré — impossible d\'envoyer via Brevo.')
            if not self.fail_silently:
                raise ValueError('BREVO_API_KEY non configuré.')
            return 0

        sent = 0
        for message in email_messages:
            try:
                payload = {
                    'sender': {
                        'name': getattr(settings, 'SGHL_ETABLISSEMENT', 'SGHL'),
                        'email': message.from_email or settings.DEFAULT_FROM_EMAIL,
                    },
                    'to': [{'email': addr} for addr in message.to],
                    'subject': message.subject,
                    'textContent': message.body or '',
                }
                for alt, mimetype in getattr(message, 'alternatives', []):
                    if mimetype == 'text/html':
                        payload['htmlContent'] = alt
                        break

                response = requests.post(
                    'https://api.brevo.com/v3/smtp/email',
                    headers={
                        'api-key': api_key,
                        'accept': 'application/json',
                        'content-type': 'application/json',
                    },
                    json=payload,
                    timeout=getattr(settings, 'EMAIL_TIMEOUT', 15),
                )
                response.raise_for_status()
                sent += 1
            except Exception:
                logger.exception('Échec envoi Brevo vers %s', message.to)
                if not self.fail_silently:
                    raise
        return sent

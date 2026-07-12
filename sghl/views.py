from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponseForbidden


def health_check(request):
    """Simple healthcheck endpoint.

    Returns basic status and whether DEBUG is enabled. Keep this lightweight
    and unauthenticated for local dev; protect or restrict in production.
    """
    return JsonResponse({
        'status': 'ok',
        'debug': bool(settings.DEBUG),
    })


def health_email_config(request):
    """Diagnostic e-mail (sans secret) — vérifie que SMTP est configuré sur Render."""
    password = (getattr(settings, 'EMAIL_HOST_PASSWORD', '') or '').strip()
    return JsonResponse({
        'status': 'ok',
        'otp_mode': getattr(settings, 'OTP_MODE', ''),
        'email_backend': settings.EMAIL_BACKEND,
        'email_host': settings.EMAIL_HOST,
        'email_port': settings.EMAIL_PORT,
        'email_user': settings.EMAIL_HOST_USER,
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'notifications_enabled': getattr(settings, 'EMAIL_NOTIFICATIONS_ENABLED', True),
        'password_configured': bool(password),
        'password_length': len(password),
    })


def health_test_email(request):
    """Envoie un e-mail de test si ?key= correspond à SGHL_DIAGNOSTIC_KEY (pas de Shell Render)."""
    expected = (getattr(settings, 'SGHL_DIAGNOSTIC_KEY', '') or '').strip()
    provided = (request.GET.get('key') or '').strip()
    if not expected or provided != expected:
        return HttpResponseForbidden('Clé diagnostic invalide.')

    to_addr = (request.GET.get('to') or settings.DEFAULT_FROM_EMAIL or '').strip()
    if not to_addr:
        return JsonResponse({'status': 'error', 'detail': 'Destinataire vide.'}, status=400)

    try:
        send_mail(
            subject='[SGHL] Test SMTP Render',
            message='Test SMTP depuis Render — si vous recevez ceci, la prod envoie bien les e-mails.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_addr],
            fail_silently=False,
        )
    except Exception as exc:
        return JsonResponse({'status': 'error', 'detail': str(exc)}, status=500)

    return JsonResponse({'status': 'ok', 'detail': f'E-mail de test envoyé à {to_addr}.'})

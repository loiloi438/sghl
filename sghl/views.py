from django.conf import settings
from django.http import JsonResponse


def health_check(request):
    """Simple healthcheck endpoint.

    Returns basic status and whether DEBUG is enabled. Keep this lightweight
    and unauthenticated for local dev; protect or restrict in production.
    """
    return JsonResponse({
        'status': 'ok',
        'debug': bool(settings.DEBUG),
    })

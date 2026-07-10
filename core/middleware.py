import time

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse


class ApiRateLimitMiddleware:
    """Rate limiting global sur les routes /api/v1/ (hors login déjà limité)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not getattr(settings, 'API_RATE_LIMIT_ENABLED', True):
            return self.get_response(request)
        path = request.path
        if not path.startswith('/api/v1/'):
            return self.get_response(request)
        exempt_suffixes = (
            '/auth/login/',
            '/sante/',
            '/healthz/',
            '/payments/webhook/',
        )
        if any(path.endswith(s) for s in exempt_suffixes):
            return self.get_response(request)

        ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR', 'unknown')
        window = getattr(settings, 'API_RATE_LIMIT_WINDOW_SECONDS', 60)
        max_requests = getattr(settings, 'API_RATE_LIMIT_MAX_REQUESTS', 120)
        bucket = int(time.time()) // window
        key = f'api_rl:{ip}:{bucket}'
        count = cache.get(key, 0)
        if count >= max_requests:
            return JsonResponse(
                {'detail': 'Trop de requêtes. Réessayez plus tard.'},
                status=429,
            )
        cache.set(key, count + 1, timeout=window + 5)
        return self.get_response(request)

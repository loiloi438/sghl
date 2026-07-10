from django.conf import settings
from django.core.cache import cache


def _fail_key(ip: str, username: str) -> str:
    return f'login_fail:{ip}:{username.lower()}'


def is_login_blocked(ip: str, username: str) -> bool:
    if not settings.LOGIN_RATE_LIMIT_ENABLED:
        return False
    fails = cache.get(_fail_key(ip, username), 0)
    return fails >= settings.LOGIN_RATE_LIMIT_MAX_ATTEMPTS


def record_login_failure(ip: str, username: str) -> None:
    if not settings.LOGIN_RATE_LIMIT_ENABLED:
        return
    key = _fail_key(ip, username)
    fails = cache.get(key, 0) + 1
    cache.set(key, fails, settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS)


def clear_login_failures(ip: str, username: str) -> None:
    cache.delete(_fail_key(ip, username))

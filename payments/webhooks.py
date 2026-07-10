import hmac
import hashlib
import logging
from typing import Optional
from django.conf import settings
import time

from typing import Tuple

logger = logging.getLogger(__name__)


def _get_secret_for_provider(provider: str) -> Optional[str]:
    # Look for env var like PAYMENTS_STRIPE_WEBHOOK_SECRET or PAYMENTS_MTN_WEBHOOK_SECRET
    key = f'PAYMENTS_{provider.upper()}_WEBHOOK_SECRET'
    return getattr(settings, key, None) or None


def verify_webhook_signature(provider: str, request) -> bool:
    """Verify HMAC-SHA256 signature for incoming webhook.

    Behavior:
    - If no secret is configured for provider, skip verification (returns True).
    - Expects header `X-Payments-Signature` containing hex HMAC-SHA256 of raw body.
    """
    secret = _get_secret_for_provider(provider)
    if not secret:
        # No secret configured -> allow for backwards compatibility in tests/dev
        logger.debug('No webhook secret configured for provider %s; skipping verification', provider)
        return True

    # Read raw body bytes from underlying Django request where possible
    raw_body = None
    django_req = getattr(request, '_request', None) or request
    if hasattr(django_req, 'body'):
        raw_body = django_req.body
    else:
        raw_body = getattr(request, 'body', None)

    if isinstance(raw_body, str):
        raw_body = raw_body.encode('utf-8')
    if raw_body is None:
        raw_body = b''

    # Special-case Stripe: signature header format is "t=<ts>,v1=<sig>" and the
    # signed payload is "{timestamp}.{raw_body}" (HMAC-SHA256)
    if provider.lower() == 'stripe':
        header = request.headers.get('Stripe-Signature') or request.META.get('HTTP_STRIPE_SIGNATURE')
        if not header:
            logger.warning('Missing Stripe-Signature header')
            return False
        try:
            ts, sig = _parse_stripe_signature(header)
        except ValueError:
            logger.warning('Invalid Stripe-Signature header format')
            return False
        expected = hmac.new(secret.encode('utf-8'), (f"{ts}.".encode('utf-8') + raw_body), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, sig):
            logger.warning('Invalid stripe webhook signature: expected %s got %s', expected, sig)
            return False
        try:
            ts_i = int(ts)
        except Exception:
            return False
        if abs(time.time() - ts_i) > 300:
            logger.warning('Stripe webhook timestamp outside tolerance')
            return False
        return True

    header = request.headers.get('X-Payments-Signature') or request.META.get('HTTP_X_PAYMENTS_SIGNATURE')
    if not header:
        logger.warning('Missing X-Payments-Signature header for provider %s', provider)
        return False

    computed = hmac.new(secret.encode('utf-8'), raw_body, hashlib.sha256).hexdigest()
    verified = hmac.compare_digest(computed, header)
    if not verified:
        logger.warning('Invalid webhook signature for provider %s: expected %s got %s', provider, computed, header)
    return verified


def _parse_stripe_signature(header: str) -> Tuple[str, str]:
    # Example header: "t=1492774577,v1=5257a869e7..."
    parts = header.split(',')
    ts = None
    sig = None
    for p in parts:
        if p.startswith('t='):
            ts = p.split('=', 1)[1]
        if p.startswith('v1='):
            sig = p.split('=', 1)[1]
    if not ts or not sig:
        raise ValueError('bad header')
    return ts, sig

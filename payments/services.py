from typing import Optional, Dict, Any
from django.db import transaction
from .models import Payment, PaymentProvider, PaymentStatus
from .models import PaymentAudit
from .providers import StripeAdapter, MobileMoneyAdapter, AggregatorMobileMoneyAdapter, FlutterwaveAdapter
from django.utils.crypto import get_random_string
import logging
from django.conf import settings
from payments.invoice_settlement import try_settle_payment_for_facture

logger = logging.getLogger(__name__)


def _adapter_for(provider: str):
    """Return an adapter for the given provider.

    Prefer an aggregator adapter if configured via settings.
    """
    provider = (provider or '').lower()
    # Mobile Money aggregator configuration example:
    # PAYMENTS_MTN_AGGREGATOR_URL, PAYMENTS_MTN_AGGREGATOR_KEY
    if provider == PaymentProvider.MTN:
        url = getattr(settings, 'PAYMENTS_MTN_AGGREGATOR_URL', None)
        key = getattr(settings, 'PAYMENTS_MTN_AGGREGATOR_KEY', None)
        # Support Flutterwave-specific aggregator configuration
        fw_url = getattr(settings, 'PAYMENTS_MTN_FLUTTERWAVE_URL', None)
        fw_key = getattr(settings, 'PAYMENTS_MTN_FLUTTERWAVE_KEY', None)
        if fw_url and fw_key:
            return FlutterwaveAdapter(base_url=fw_url, api_key=fw_key, provider_name='mtn')
        if url and key:
            return AggregatorMobileMoneyAdapter(base_url=url, api_key=key, provider_name='mtn')
        return MobileMoneyAdapter('mtn')
    if provider == PaymentProvider.AIRTEL:
        url = getattr(settings, 'PAYMENTS_AIRTEL_AGGREGATOR_URL', None)
        key = getattr(settings, 'PAYMENTS_AIRTEL_AGGREGATOR_KEY', None)
        if url and key:
            return AggregatorMobileMoneyAdapter(base_url=url, api_key=key, provider_name='airtel')
        return MobileMoneyAdapter('airtel')
    if provider == PaymentProvider.STRIPE:
        stripe_key = getattr(settings, 'PAYMENTS_STRIPE_SECRET_KEY', None)
        return StripeAdapter(api_key=stripe_key)
    return None


def initiate_payment(*, provider: str, amount_cents: int, currency: str = 'XAF', user=None, metadata: Optional[Dict[str, Any]] = None) -> Payment:
    metadata = metadata or {}
    reference = metadata.get('reference') or get_random_string(12)
    with transaction.atomic():
        payment = Payment.objects.create(
            provider=provider,
            amount_cents=amount_cents,
            currency=currency,
            reference=reference,
            metadata=metadata,
            user=user,
        )

        adapter = _adapter_for(provider)
        if not adapter:
            payment.status = PaymentStatus.FAILED
            payment.save(update_fields=['status'])
            raise RuntimeError(f'No adapter for provider {provider}')

        # Generate a reproducible idempotency key per reference/provider
        idempotency_key = f"{provider}:{reference}"
        result = adapter.create_payment(reference=reference, amount_cents=amount_cents, currency=currency, metadata=metadata, idempotency_key=idempotency_key)
        external_id = result.get('external_id')
        status = result.get('status') or 'pending'

        previous = payment.status
        payment.external_id = external_id
        payment.status = status
        payment.metadata = {**(payment.metadata or {}), 'provider_raw': result.get('raw')}
        payment.save(update_fields=['external_id', 'status', 'metadata'])

        # Record audit
        PaymentAudit.objects.create(
            payment=payment,
            previous_status=previous,
            new_status=payment.status,
            event='initiate_payment',
            metadata={'provider_raw': result.get('raw')},
            actor=user if hasattr(user, 'id') else None,
        )

    logger.info('Initiated payment %s -> %s', payment.reference, payment.status)
    return payment


def poll_and_finalize(payment_id):
    try:
        payment = Payment.objects.get(pk=payment_id)
    except Payment.DoesNotExist:
        return None
    adapter = _adapter_for(payment.provider)
    if not adapter:
        return payment
    result = adapter.retrieve_payment(payment.external_id)
    status = result.get('status')
    if status == 'success':
        previous = payment.status
        payment.status = PaymentStatus.SUCCESS
    elif status == 'failed':
        previous = payment.status
        payment.status = PaymentStatus.FAILED
    payment.metadata = {**(payment.metadata or {}), 'provider_last': result}
    payment.save(update_fields=['status', 'metadata'])

    # Audit record
    try:
        PaymentAudit.objects.create(
            payment=payment,
            previous_status=previous,
            new_status=payment.status,
            event='poll_and_finalize',
            metadata={'provider_last': result},
        )
    except Exception:
        logger.exception('Failed to create PaymentAudit')
    if payment.status == PaymentStatus.SUCCESS:
        try_settle_payment_for_facture(payment)
    return payment

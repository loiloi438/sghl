from typing import Optional, Dict, Any
from ninja import Router, Schema
from ninja.errors import HttpError

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from payments.services import initiate_payment, poll_and_finalize
from payments.invoice_settlement import try_settle_payment_for_facture
from payments.models import Payment
from payments.webhooks import verify_webhook_signature

router = Router(tags=['Paiements'])
jwt_auth = JWTAuth()

ROLES_PAIEMENT = {Role.ADMIN, Role.COMPTABLE, Role.PATIENT}


class CreatePaymentIn(Schema):
    provider: str
    amount_cents: int
    currency: Optional[str] = 'XAF'
    metadata: Optional[Dict[str, Any]] = None


class PaymentOut(Schema):
    reference: str
    provider: str
    amount_cents: int
    currency: str
    status: str
    external_id: Optional[str]
    client_secret: Optional[str] = None
    redirect_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post('/payments/create/', response=PaymentOut, auth=jwt_auth)
def create_payment(request, payload: CreatePaymentIn):
    user = request.auth
    if user.role not in ROLES_PAIEMENT:
        raise HttpError(403, 'Accès refusé.')
    try:
        payment = initiate_payment(
            provider=payload.provider,
            amount_cents=payload.amount_cents,
            currency=payload.currency,
            user=user,
            metadata=payload.metadata,
        )
    except Exception as exc:
        raise HttpError(400, str(exc)) from exc

    provider_raw = payment.metadata.get('provider_raw') if payment.metadata else None
    client_secret = None
    redirect_url = None
    if isinstance(provider_raw, dict):
        client_secret = provider_raw.get('client_secret')
        redirect_url = provider_raw.get('redirect_url')

    return PaymentOut(
        reference=payment.reference,
        provider=payment.provider,
        amount_cents=payment.amount_cents,
        currency=payment.currency,
        status=payment.status,
        external_id=payment.external_id,
        client_secret=client_secret,
        redirect_url=redirect_url,
        metadata=payment.metadata,
    )


class WebhookIn(Schema):
    provider: str
    external_id: str
    status: str
    raw: Optional[Dict[str, Any]] = None


@router.post('/payments/webhook/')
def payments_webhook(request, payload: WebhookIn):
    # Verify webhook signature (if configured) then process
    try:
        if not verify_webhook_signature(payload.provider, request):
            raise HttpError(400, 'Invalid webhook signature')
    except HttpError:
        raise
    except Exception:
        raise HttpError(400, 'Webhook verification failed')

    # Simple webhook receiver for simulated providers: find payment by external_id
    try:
        payment = Payment.objects.filter(external_id=payload.external_id).first()
        if not payment:
            raise HttpError(404, 'Payment not found')

        # Map incoming status to our status
        if payload.status.lower() in ('success', 'completed'):
            payment.status = 'success'
        elif payload.status.lower() in ('failed', 'cancelled'):
            payment.status = 'failed'
        else:
            payment.status = 'pending'

        payment.metadata = {**(payment.metadata or {}), 'webhook': payload.raw}
        payment.save()

        if payment.status == 'success':
            try_settle_payment_for_facture(payment)
    except HttpError:
        raise
    except Exception as exc:
        raise HttpError(500, str(exc)) from exc

    return {'detail': 'ok'}


@router.get('/payments/{reference}/status/', auth=jwt_auth)
def payment_status(request, reference: str):
    if request.auth.role not in ROLES_PAIEMENT:
        raise HttpError(403, 'Accès refusé.')
    payment = Payment.objects.filter(reference=reference).first()
    if not payment:
        raise HttpError(404, 'Payment not found')
    # Optionally poll provider to update async flows
    if payment.status == 'pending' and payment.external_id:
        payment = poll_and_finalize(payment.id)
    if payment.status == 'success':
        payment = try_settle_payment_for_facture(payment)
    meta = payment.metadata or {}
    return {
        'reference': payment.reference,
        'status': payment.status,
        'external_id': payment.external_id,
        'facture_settled': bool(meta.get('facture_settled')),
        'settlement_error': meta.get('settlement_error'),
    }

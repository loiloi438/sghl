from decimal import Decimal

from django.db import transaction

from facturation.models import Facture, StatutFacture
from facturation.services import FacturationError, enregistrer_paiement_en_ligne
from payments.models import Payment, PaymentStatus

import logging

logger = logging.getLogger(__name__)


def _mode_for_provider(provider: str) -> str:
    if provider == 'stripe':
        return 'carte'
    return 'mobile_money'


def payment_covers_facture(payment: Payment, facture: Facture) -> bool:
    meta = payment.metadata or {}
    return str(meta.get('facture_id')) == str(facture.id)


def has_pending_facture_payment(facture_id) -> bool:
    return Payment.objects.filter(
        status=PaymentStatus.PENDING,
        metadata__facture_id=str(facture_id),
    ).exists()


@transaction.atomic
def try_settle_payment_for_facture(payment: Payment) -> Payment:
    if payment.status != PaymentStatus.SUCCESS:
        return payment

    meta = dict(payment.metadata or {})
    if meta.get('facture_settled'):
        return payment

    facture_id = meta.get('facture_id')
    if not facture_id:
        return payment

    utilisateur = payment.user
    if utilisateur is None:
        logger.warning('Payment %s success without user; cannot settle facture', payment.reference)
        return payment

    try:
        facture = Facture.objects.select_related('hospitalisation__patient').get(pk=facture_id)
    except Facture.DoesNotExist:
        meta['settlement_error'] = 'Facture introuvable.'
        payment.metadata = meta
        payment.save(update_fields=['metadata', 'updated_at'])
        return payment

    if facture.statut == StatutFacture.PAYEE:
        meta['facture_settled'] = True
        payment.metadata = meta
        payment.save(update_fields=['metadata', 'updated_at'])
        return payment

    montant = (Decimal(payment.amount_cents) / Decimal('100')).quantize(Decimal('0.01'))
    version = int(meta.get('facture_version', facture.version))

    try:
        enregistrer_paiement_en_ligne(
            facture=facture,
            utilisateur=utilisateur,
            version=version,
            mode_paiement=_mode_for_provider(payment.provider),
            reference_paiement=payment.reference,
            montant=montant,
        )
        meta['facture_settled'] = True
        meta.pop('settlement_error', None)
        logger.info('Facture %s soldée via paiement %s', facture_id, payment.reference)
    except FacturationError as exc:
        meta['settlement_error'] = exc.message
        logger.warning('Échec règlement facture %s: %s', facture_id, exc.message)

    payment.metadata = meta
    payment.save(update_fields=['metadata', 'updated_at'])
    return payment

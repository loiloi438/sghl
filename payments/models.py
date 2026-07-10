import uuid
from django.conf import settings
from django.db import models


class PaymentProvider(models.TextChoices):
    STRIPE = 'stripe', 'Stripe'
    MTN = 'mtn', 'MTN Mobile Money'
    AIRTEL = 'airtel', 'Airtel Money'
    PAYPAL = 'paypal', 'PayPal'


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    SUCCESS = 'success', 'Success'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=30, choices=PaymentProvider.choices)
    amount_cents = models.BigIntegerField()
    currency = models.CharField(max_length=6, default='XAF')
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    reference = models.CharField(max_length=128, unique=True)
    external_id = models.CharField(max_length=128, blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.reference} ({self.provider}) {self.status} {self.amount_cents / 100:.2f} {self.currency}"


class PaymentAudit(models.Model):
    payment = models.ForeignKey('payments.Payment', on_delete=models.CASCADE, related_name='audits')
    previous_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20)
    event = models.CharField(max_length=64, blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Audit {self.payment.reference}: {self.previous_status} -> {self.new_status} @ {self.created_at.isoformat()}"

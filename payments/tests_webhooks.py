from django.test import TestCase, override_settings
from ninja.testing import TestClient

from api.v1.router import api
from payments.models import Payment
from payments.test_helpers import payment_auth_headers
import json
import hmac
import hashlib
import time


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', EMAIL_NOTIFICATIONS_ENABLED=True)
class PaymentsWebhookTests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.headers = payment_auth_headers()

    def test_mobile_money_webhook_updates_payment(self):
        res = self.client.post(
            '/payments/create/',
            json={'provider': 'mtn', 'amount_cents': 15000, 'currency': 'XAF'},
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 200, res.content)
        body = res.json()
        payment = Payment.objects.get(reference=body['reference'])
        self.assertEqual(payment.provider, 'mtn')
        self.assertEqual(payment.status, 'pending')

        hook = {'provider': 'mtn', 'external_id': payment.external_id, 'status': 'success', 'raw': {'simulated': True}}
        raw = json.dumps(hook).encode('utf-8')
        secret = 'test_mtn_secret'
        signature = hmac.new(secret.encode('utf-8'), raw, hashlib.sha256).hexdigest()

        with override_settings(PAYMENTS_MTN_WEBHOOK_SECRET=secret):
            wh = self.client.post('/payments/webhook/', json=hook, headers={'X-Payments-Signature': signature})
        self.assertEqual(wh.status_code, 200, wh.content)

        payment.refresh_from_db()
        self.assertEqual(payment.status, 'success')
        self.assertIn('webhook', payment.metadata or {})

    def test_stripe_webhook_noop_if_missing(self):
        res = self.client.post(
            '/payments/create/',
            json={'provider': 'stripe', 'amount_cents': 20000, 'currency': 'XAF'},
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 200, res.content)
        payment = Payment.objects.get(reference=res.json()['reference'])
        self.assertEqual(payment.status, 'success')

        hook = {'provider': 'stripe', 'external_id': 'stripe_unknown', 'status': 'success', 'raw': {}}
        raw = json.dumps(hook).encode('utf-8')
        secret = 'test_stripe_secret'
        ts = str(int(time.time()))
        sig = hmac.new(secret.encode('utf-8'), (f"{ts}.".encode('utf-8') + raw), hashlib.sha256).hexdigest()
        header = f"t={ts},v1={sig}"

        with override_settings(PAYMENTS_STRIPE_WEBHOOK_SECRET=secret):
            wh = self.client.post('/payments/webhook/', json=hook, headers={'Stripe-Signature': header})
        self.assertEqual(wh.status_code, 404)

    def test_stripe_webhook_signature_validation(self):
        res = self.client.post(
            '/payments/create/',
            json={'provider': 'stripe', 'amount_cents': 20000, 'currency': 'XAF'},
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 200, res.content)
        payment = Payment.objects.get(reference=res.json()['reference'])

        hook = {'provider': 'stripe', 'external_id': payment.external_id, 'status': 'success', 'raw': {}}
        raw = json.dumps(hook).encode('utf-8')
        secret = 'test_stripe_secret'
        ts = str(int(time.time()))
        sig = hmac.new(secret.encode('utf-8'), (f"{ts}.".encode('utf-8') + raw), hashlib.sha256).hexdigest()
        header = f"t={ts},v1={sig}"

        with override_settings(**{'PAYMENTS_STRIPE_WEBHOOK_SECRET': secret}):
            wh = self.client.post('/payments/webhook/', json=hook, headers={'Stripe-Signature': header})
            self.assertEqual(wh.status_code, 200, wh.content)

        with override_settings(**{'PAYMENTS_STRIPE_WEBHOOK_SECRET': secret}):
            wh2 = self.client.post('/payments/webhook/', json=hook, headers={'Stripe-Signature': 't=123,v1=bad'})
            self.assertEqual(wh2.status_code, 400)

    def test_mobile_money_webhook_signature_validation(self):
        res = self.client.post(
            '/payments/create/',
            json={'provider': 'mtn', 'amount_cents': 15000, 'currency': 'XAF'},
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 200, res.content)
        payment = Payment.objects.get(reference=res.json()['reference'])
        self.assertEqual(payment.status, 'pending')

        hook = {'provider': 'mtn', 'external_id': payment.external_id, 'status': 'success', 'raw': {'simulated': True}}
        raw = json.dumps(hook).encode('utf-8')
        secret = 'test_mtn_secret'
        signature = hmac.new(secret.encode('utf-8'), raw, hashlib.sha256).hexdigest()

        with override_settings(**{'PAYMENTS_MTN_WEBHOOK_SECRET': secret}):
            wh = self.client.post('/payments/webhook/', json=hook, headers={'X-Payments-Signature': signature})
            self.assertEqual(wh.status_code, 200, wh.content)

        with override_settings(**{'PAYMENTS_MTN_WEBHOOK_SECRET': secret}):
            wh2 = self.client.post('/payments/webhook/', json=hook, headers={'X-Payments-Signature': 'bad'})
            self.assertEqual(wh2.status_code, 400)

from django.test import TestCase, override_settings
from ninja.testing import TestClient

from api.v1.router import api
from payments.test_helpers import payment_auth_headers


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', EMAIL_NOTIFICATIONS_ENABLED=True)
class PaymentsApiTests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.headers = payment_auth_headers()

    def test_create_stripe_payment(self):
        res = self.client.post(
            '/payments/create/',
            json={'provider': 'stripe', 'amount_cents': 50000, 'currency': 'XAF'},
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 200, res.content)
        body = res.json()
        self.assertIn('reference', body)
        self.assertEqual(body['status'], 'success')

    def test_create_mobilemoney_payment(self):
        res = self.client.post(
            '/payments/create/',
            json={'provider': 'mtn', 'amount_cents': 10000, 'currency': 'XAF'},
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 200, res.content)
        body = res.json()
        self.assertIn('reference', body)
        self.assertIn(body['status'], ('pending', 'success'))

    def test_anonymous_rejected(self):
        res = self.client.post(
            '/payments/create/',
            json={'provider': 'stripe', 'amount_cents': 1000, 'currency': 'XAF'},
        )
        self.assertEqual(res.status_code, 401)

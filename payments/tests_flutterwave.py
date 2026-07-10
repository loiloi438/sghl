from django.test import TestCase, override_settings
from ninja.testing import TestClient
from unittest.mock import patch, MagicMock

from api.v1.router import api
from payments.models import Payment
from payments.test_helpers import payment_auth_headers


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', EMAIL_NOTIFICATIONS_ENABLED=True)
class FlutterwaveAdapterTests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.headers = payment_auth_headers()

    def test_flutterwave_create_and_retrieve(self):
        fake_post = MagicMock()
        fake_post.status_code = 200
        fake_post.json.return_value = {'status': 'success', 'data': {'id': 'fw_123', 'status': 'pending'}}

        fake_get = MagicMock()
        fake_get.status_code = 200
        fake_get.json.return_value = {'status': 'success', 'data': {'id': 'fw_123', 'status': 'success'}}

        with override_settings(PAYMENTS_MTN_FLUTTERWAVE_URL='https://api.fw', PAYMENTS_MTN_FLUTTERWAVE_KEY='k'):
            with patch('payments.providers.requests.post', return_value=fake_post):
                res = self.client.post(
                    '/payments/create/',
                    json={'provider': 'mtn', 'amount_cents': 5000, 'currency': 'XAF'},
                    headers=self.headers,
                )
                self.assertEqual(res.status_code, 200)
                payment = Payment.objects.get(reference=res.json()['reference'])
                self.assertEqual(payment.external_id, 'fw_123')

            with patch('payments.providers.requests.get', return_value=fake_get):
                st = self.client.get(f"/payments/{payment.reference}/status/", headers=self.headers)
                self.assertEqual(st.status_code, 200)
                self.assertEqual(st.json()['status'], 'success')

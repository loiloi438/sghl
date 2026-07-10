from django.test import TestCase, override_settings
from ninja.testing import TestClient
from unittest.mock import patch, MagicMock

from api.v1.router import api
from payments.models import Payment
from payments.test_helpers import payment_auth_headers


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', EMAIL_NOTIFICATIONS_ENABLED=True)
class AggregatorAdapterTests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.headers = payment_auth_headers()

    def test_initiate_payment_uses_aggregator(self):
        fake_resp = MagicMock()
        fake_resp.status_code = 200
        fake_resp.json.return_value = {'external_id': 'agg_123', 'status': 'pending'}

        with override_settings(PAYMENTS_MTN_AGGREGATOR_URL='https://api.agg', PAYMENTS_MTN_AGGREGATOR_KEY='secret'):
            with patch('payments.providers.requests.post', return_value=fake_resp):
                res = self.client.post(
                    '/payments/create/',
                    json={'provider': 'mtn', 'amount_cents': 1000, 'currency': 'XAF'},
                    headers=self.headers,
                )
                self.assertEqual(res.status_code, 200)
                payment = Payment.objects.get(reference=res.json()['reference'])
                self.assertEqual(payment.external_id, 'agg_123')
                self.assertEqual(payment.status, 'pending')

    def test_poll_and_finalize_calls_aggregator(self):
        fake_create = MagicMock()
        fake_create.status_code = 200
        fake_create.json.return_value = {'external_id': 'agg_999', 'status': 'pending'}

        fake_get = MagicMock()
        fake_get.status_code = 200
        fake_get.json.return_value = {'external_id': 'agg_999', 'status': 'success'}

        with override_settings(PAYMENTS_MTN_AGGREGATOR_URL='https://api.agg', PAYMENTS_MTN_AGGREGATOR_KEY='secret'):
            with patch('payments.providers.requests.post', return_value=fake_create):
                res = self.client.post(
                    '/payments/create/',
                    json={'provider': 'mtn', 'amount_cents': 1000, 'currency': 'XAF'},
                    headers=self.headers,
                )
                self.assertEqual(res.status_code, 200)
                payment = Payment.objects.get(reference=res.json()['reference'])
                self.assertEqual(payment.status, 'pending')

            with patch('payments.providers.requests.get', return_value=fake_get):
                st = self.client.get(f"/payments/{payment.reference}/status/", headers=self.headers)
                self.assertEqual(st.status_code, 200)
                self.assertEqual(st.json()['status'], 'success')

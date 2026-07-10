from django.test import TestCase, override_settings
from ninja.testing import TestClient
from unittest.mock import patch, MagicMock

from api.v1.router import api
from payments.models import Payment
from payments.test_helpers import payment_auth_headers


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', EMAIL_NOTIFICATIONS_ENABLED=True)
class PaymentAuditTests(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.headers = payment_auth_headers()

    def test_audit_on_initiate_and_poll(self):
        fake_post = MagicMock()
        fake_post.status_code = 200
        fake_post.json.return_value = {'external_id': 'agg_x', 'status': 'pending', 'data': {'id': 'agg_x'}}

        fake_get = MagicMock()
        fake_get.status_code = 200
        fake_get.json.return_value = {'external_id': 'agg_x', 'status': 'success', 'data': {'id': 'agg_x'}}

        with override_settings(PAYMENTS_MTN_AGGREGATOR_URL='https://api.agg', PAYMENTS_MTN_AGGREGATOR_KEY='k'):
            with patch('payments.providers.requests.post', return_value=fake_post):
                res = self.client.post(
                    '/payments/create/',
                    json={'provider': 'mtn', 'amount_cents': 2500, 'currency': 'XAF'},
                    headers=self.headers,
                )
                self.assertEqual(res.status_code, 200)
                p = Payment.objects.get(reference=res.json()['reference'])
                audits = list(p.audits.all())
                self.assertEqual(len(audits), 1)
                self.assertEqual(audits[0].event, 'initiate_payment')

            with patch('payments.providers.requests.get', return_value=fake_get):
                st = self.client.get(f"/payments/{p.reference}/status/", headers=self.headers)
                self.assertEqual(st.status_code, 200)
                p.refresh_from_db()
                audits = list(p.audits.all())
                self.assertTrue(any(a.event == 'poll_and_finalize' for a in audits))

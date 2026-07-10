from django.test import TestCase, override_settings
from ninja.testing import TestClient
from api.v1.router import api
from payments.test_helpers import payment_auth_headers
from payments.models import Payment
from unittest.mock import patch, MagicMock


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', EMAIL_NOTIFICATIONS_ENABLED=True)
class StripeApiTests(TestCase):
    def test_create_payment_intent_and_retrieve(self):
        client = TestClient(api)
        headers = payment_auth_headers()
        fake_post = MagicMock()
        fake_post.status_code = 200
        fake_post.json.return_value = {'id': 'pi_123', 'client_secret': 'cs_abc', 'status': 'requires_payment_method'}

        fake_get = MagicMock()
        fake_get.status_code = 200
        fake_get.json.return_value = {'id': 'pi_123', 'status': 'succeeded'}

        with override_settings(PAYMENTS_STRIPE_SECRET_KEY='sk_test_abc'):
            with patch('payments.providers.requests.post', return_value=fake_post) as post:
                res = client.post('/payments/create/', json={'provider': 'stripe', 'amount_cents': 3000, 'currency': 'XAF'}, headers=headers)
                self.assertEqual(res.status_code, 200)
                body = res.json()
                p = Payment.objects.get(reference=body['reference'])
                self.assertEqual(p.external_id, 'pi_123')
                self.assertEqual(p.metadata.get('provider_raw', {}).get('client_secret'), 'cs_abc')

            with patch('payments.providers.requests.get', return_value=fake_get):
                st = client.get(f"/payments/{p.reference}/status/", headers=headers)
                self.assertEqual(st.status_code, 200)
                self.assertEqual(st.json()['status'], 'success')

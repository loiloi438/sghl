from __future__ import annotations

from typing import Any, Dict
from abc import ABC, abstractmethod
import logging
import requests

logger = logging.getLogger(__name__)


class ProviderAdapter(ABC):
    """Abstract adapter interface for payment providers."""

    @abstractmethod
    def create_payment(self, *, reference: str, amount_cents: int, currency: str, metadata: Dict[str, Any], idempotency_key: str | None = None) -> Dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    def retrieve_payment(self, external_id: str) -> Dict[str, Any]:
        raise NotImplementedError()


class StripeAdapter(ProviderAdapter):
    """Stripe adapter. If `api_key` is provided, uses Stripe HTTP API; otherwise simulated."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def _auth_headers(self):
        if not self.api_key:
            return {}
        return {'Authorization': f'Bearer {self.api_key}'}

    def create_payment(self, *, reference: str, amount_cents: int, currency: str, metadata: Dict[str, Any], idempotency_key: str | None = None) -> Dict[str, Any]:
        if not self.api_key:
            # Simulate creating a Stripe charge / PaymentIntent
            external_id = f'stripe_{reference}'
            logger.info('Simulated Stripe create_payment %s %s', reference, amount_cents)
            return {
                'status': 'success',
                'external_id': external_id,
                'client_secret': None,
                'redirect_url': None,
                'raw': {'simulated': True},
            }

        # Real Stripe API: create PaymentIntent
        url = 'https://api.stripe.com/v1/payment_intents'
        data = {
            'amount': str(int(amount_cents)),
            'currency': currency.lower(),
            'metadata[reference]': reference,
        }
        # Flatten metadata into form fields
        for k, v in (metadata or {}).items():
            data[f'metadata[{k}]'] = str(v)

        logger.info('Creating Stripe PaymentIntent for %s', reference)
        headers = {**self._auth_headers(), 'Content-Type': 'application/x-www-form-urlencoded'}
        if idempotency_key:
            headers['Idempotency-Key'] = idempotency_key
        resp = requests.post(url, data=data, headers=headers, timeout=10)
        resp.raise_for_status()
        js = resp.json()
        stripe_status = js.get('status')
        if stripe_status == 'succeeded':
            status = 'success'
        elif stripe_status in ('requires_payment_method', 'requires_action', 'processing', 'requires_capture', 'requires_confirmation'):
            status = 'pending'
        elif stripe_status in ('canceled', 'failed'):
            status = 'failed'
        else:
            status = stripe_status or 'pending'

        return {
            'status': status,
            'external_id': js.get('id'),
            'client_secret': js.get('client_secret'),
            'raw': js,
        }

    def retrieve_payment(self, external_id: str) -> Dict[str, Any]:
        if not self.api_key:
            logger.info('Simulated Stripe retrieve_payment %s', external_id)
            return {'status': 'success', 'external_id': external_id}

        url = f'https://api.stripe.com/v1/payment_intents/{external_id}'
        resp = requests.get(url, headers=self._auth_headers(), timeout=10)
        resp.raise_for_status()
        js = resp.json()
        # Normalize Stripe statuses to our canonical ones
        stripe_status = js.get('status')
        if stripe_status == 'succeeded':
            status = 'success'
        elif stripe_status in ('requires_payment_method', 'requires_action', 'processing', 'requires_capture', 'requires_confirmation'):
            status = 'pending'
        elif stripe_status in ('canceled', 'failed'):
            status = 'failed'
        else:
            status = stripe_status
        return {'status': status, 'external_id': external_id, 'raw': js}


class MobileMoneyAdapter(ProviderAdapter):
    """Stub adapter for Mobile Money providers (Airtel/MTN)."""

    def __init__(self, provider_name: str = 'mtn'):
        self.provider_name = provider_name

    def create_payment(self, *, reference: str, amount_cents: int, currency: str, metadata: Dict[str, Any], idempotency_key: str | None = None) -> Dict[str, Any]:
        # Mobile money flows are often asynchronous: return pending + payment token
        external_id = f'{self.provider_name}_{reference}'
        logger.info('Simulated MobileMoney create_payment %s %s', reference, amount_cents)
        return {
            'status': 'pending',
            'external_id': external_id,
            'redirect_url': None,
            'raw': {'simulated': True},
        }

    def retrieve_payment(self, external_id: str) -> Dict[str, Any]:
        logger.info('Simulated MobileMoney retrieve_payment %s', external_id)
        # For simulation, treat pending -> success on retrieve
        return {'status': 'success', 'external_id': external_id}


class AggregatorMobileMoneyAdapter(ProviderAdapter):
    """Adapter for a Mobile Money aggregator API.

    The aggregator is expected to expose simple endpoints:
    - POST {base_url}/payments    -> returns JSON with 'external_id' and 'status'
    - GET  {base_url}/payments/{external_id} -> returns JSON with 'status'
    """

    def __init__(self, base_url: str, api_key: str, provider_name: str = 'mtn'):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.provider_name = provider_name

    def _headers(self):
        return {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}

    def create_payment(self, *, reference: str, amount_cents: int, currency: str, metadata: Dict[str, Any], idempotency_key: str | None = None) -> Dict[str, Any]:
        url = f"{self.base_url}/payments"
        payload = {
            'provider': self.provider_name,
            'reference': reference,
            'amount_cents': amount_cents,
            'currency': currency,
            'metadata': metadata or {},
        }
        logger.info('Aggregator create_payment POST %s', url)
        headers = self._headers()
        if idempotency_key:
            headers['Idempotency-Key'] = idempotency_key
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            'status': data.get('status', 'pending'),
            'external_id': data.get('external_id'),
            'raw': data,
        }

    def retrieve_payment(self, external_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/payments/{external_id}"
        logger.info('Aggregator retrieve_payment GET %s', url)
        resp = requests.get(url, headers=self._headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return {
            'status': data.get('status', 'pending'),
            'external_id': external_id,
            'raw': data,
        }


class FlutterwaveAdapter(ProviderAdapter):
    """Example adapter for Flutterwave-like aggregator.

    This is an example mapping: it posts to {base_url}/v3/payments and retrieves
    via {base_url}/v3/transactions/{id} or queries by tx_ref. The exact API may
    differ per provider; adapt as necessary for the real aggregator.
    """

    def __init__(self, base_url: str, api_key: str, currency: str = 'XAF', provider_name: str = 'mtn'):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.currency = currency
        self.provider_name = provider_name

    def _headers(self):
        return {'Authorization': f'Bearer {self.api_key}', 'Content-Type': 'application/json'}

    def create_payment(self, *, reference: str, amount_cents: int, currency: str, metadata: Dict[str, Any], idempotency_key: str | None = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v3/payments"
        amount = amount_cents / 100.0
        payload = {
            'tx_ref': reference,
            'amount': f"{amount:.2f}",
            'currency': currency,
            'payment_type': 'mobile_money',
            'provider': self.provider_name,
            'metadata': metadata or {},
        }
        headers = self._headers()
        if idempotency_key:
            headers['Idempotency-Key'] = idempotency_key
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Flutterwave returns nested structure; adapt as needed
        external_id = data.get('data', {}).get('id') or data.get('transaction_id') or data.get('external_id')
        status = data.get('status') or data.get('data', {}).get('status', 'pending')
        return {'status': status, 'external_id': external_id, 'raw': data}

    def retrieve_payment(self, external_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v3/transactions/{external_id}"
        resp = requests.get(url, headers=self._headers(), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        status = data.get('status') or data.get('data', {}).get('status', 'pending')
        return {'status': status, 'external_id': external_id, 'raw': data}

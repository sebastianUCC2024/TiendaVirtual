import stripe
from decimal import Decimal
from typing import Optional
from django.conf import settings

from .base import PaymentProcessor, PaymentIntentResult, WebhookResult
from apps.payments.exceptions import PaymentException, WebhookException


class StripeAdapter(PaymentProcessor):
    """
    Adapter que encapsula toda la lógica específica de Stripe.
    Si Stripe cambia su API, solo se modifica este archivo.
    """

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def _to_cents(self, amount: Decimal) -> int:
        """Stripe trabaja en centavos (enteros)."""
        return int(amount * 100)

    def create_payment_intent(
        self,
        amount: Decimal,
        currency: str = 'cop',
        metadata: Optional[dict] = None
    ) -> PaymentIntentResult:
        try:
            intent = stripe.PaymentIntent.create(
                amount=self._to_cents(amount),
                currency=currency.lower(),
                metadata=metadata or {},
                automatic_payment_methods={'enabled': True},
            )
            return PaymentIntentResult(
                payment_intent_id=intent.id,
                client_secret=intent.client_secret,
                status=intent.status,
                amount=amount,
                currency=currency,
            )
        except stripe.StripeError as e:
            raise PaymentException(str(e)) from e

    def confirm_payment(self, payment_intent_id: str) -> dict:
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {'status': intent.status, 'id': intent.id}
        except stripe.StripeError as e:
            raise PaymentException(str(e)) from e

    def refund(self, payment_intent_id: str, amount: Optional[Decimal] = None) -> dict:
        try:
            params = {'payment_intent': payment_intent_id}
            if amount:
                params['amount'] = self._to_cents(amount)
            refund = stripe.Refund.create(**params)
            return {'refund_id': refund.id, 'status': refund.status}
        except stripe.StripeError as e:
            raise PaymentException(str(e)) from e

    def handle_webhook(self, payload: bytes, signature: str) -> WebhookResult:
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.SignatureVerificationError) as e:
            raise WebhookException(str(e)) from e

        payment_intent_id = ''
        status = ''

        if event.type in ('payment_intent.succeeded', 'payment_intent.payment_failed',
                          'payment_intent.canceled'):
            pi = event.data.object
            payment_intent_id = pi.id
            status = pi.status

        return WebhookResult(
            event_type=event.type,
            payment_intent_id=payment_intent_id,
            status=status,
            raw_event=dict(event),
        )

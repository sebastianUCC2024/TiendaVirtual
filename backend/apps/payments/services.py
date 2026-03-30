from django.db import transaction
from django.conf import settings
from rest_framework.exceptions import ValidationError, NotFound

from .models import Payment, Transaction
from .processors.factory import PaymentProcessorFactory
from .exceptions import PaymentException, WebhookException
from apps.orders.models import Order
from apps.users.models import User


class PaymentService:

    @staticmethod
    @transaction.atomic
    def create_payment_intent(user: User, order_id: int, provider: str = 'stripe') -> dict:
        """
        Crea un PaymentIntent en el proveedor y registra el pago en BD.
        Retorna client_secret y publishable_key para el frontend.
        """
        try:
            order = Order.objects.select_for_update().get(id=order_id, user=user)
        except Order.DoesNotExist:
            raise NotFound('Pedido no encontrado.')

        if order.status not in (Order.Status.PENDING, Order.Status.PAYMENT_PENDING):
            raise ValidationError('Este pedido no puede ser pagado en su estado actual.')

        # Evitar crear múltiples PaymentIntents para la misma orden
        if hasattr(order, 'payment') and order.payment.status == Payment.Status.APPROVED:
            raise ValidationError('Este pedido ya fue pagado.')

        processor = PaymentProcessorFactory.get_processor(provider)

        try:
            result = processor.create_payment_intent(
                amount=order.total,
                currency='cop',
                metadata={'order_id': str(order.id), 'order_number': order.order_number}
            )
        except PaymentException as e:
            raise ValidationError(f'Error al crear el pago: {str(e)}')

        # Crear o actualizar el registro de pago
        payment, _ = Payment.objects.update_or_create(
            order=order,
            defaults={
                'provider': provider,
                'payment_intent_id': result.payment_intent_id,
                'client_secret': result.client_secret,
                'amount': order.total,
                'currency': 'COP',
                'status': Payment.Status.PROCESSING,
            }
        )

        Transaction.objects.create(
            payment=payment,
            event_type=Transaction.EventType.CREATED,
            provider_event_id=result.payment_intent_id,
            raw_response={'status': result.status},
        )

        return {
            'payment_id': payment.id,
            'client_secret': result.client_secret,
            'payment_intent_id': result.payment_intent_id,
            'amount': order.total,
            'currency': 'COP',
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        }

    @staticmethod
    @transaction.atomic
    def process_webhook(payload: bytes, signature: str, provider: str = 'stripe') -> None:
        """
        Recibe y procesa un webhook del proveedor de pago.
        Actualiza el estado del pago y del pedido automáticamente.
        """
        processor = PaymentProcessorFactory.get_processor(provider)

        try:
            result = processor.handle_webhook(payload, signature)
        except WebhookException as e:
            raise ValidationError(f'Webhook inválido: {str(e)}')

        if not result.payment_intent_id:
            return  # Evento que no nos interesa

        try:
            payment = Payment.objects.select_related('order').get(
                payment_intent_id=result.payment_intent_id
            )
        except Payment.DoesNotExist:
            return  # Pago no registrado en nuestro sistema

        # Registrar la transacción del webhook
        Transaction.objects.create(
            payment=payment,
            event_type=Transaction.EventType.WEBHOOK,
            provider_event_id=result.payment_intent_id,
            raw_response=result.raw_event,
        )

        # Mapear estado del proveedor a nuestro dominio
        PaymentService._update_payment_status(payment, result.event_type)

    @staticmethod
    def _update_payment_status(payment: Payment, event_type: str) -> None:
        order = payment.order

        if event_type == 'payment_intent.succeeded':
            payment.status = Payment.Status.APPROVED
            order.status = Order.Status.PAYMENT_APPROVED
            Transaction.objects.create(
                payment=payment,
                event_type=Transaction.EventType.CONFIRMED,
                raw_response={'event': event_type},
            )

        elif event_type in ('payment_intent.payment_failed', 'payment_intent.canceled'):
            payment.status = Payment.Status.REJECTED
            order.status = Order.Status.PAYMENT_REJECTED
            Transaction.objects.create(
                payment=payment,
                event_type=Transaction.EventType.FAILED,
                raw_response={'event': event_type},
            )

        payment.save(update_fields=['status', 'updated_at'])
        order.save(update_fields=['status', 'updated_at'])

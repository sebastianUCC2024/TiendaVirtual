import pytest
from decimal import Decimal
from unittest.mock import patch, MagicMock
from apps.payments.services import PaymentService
from apps.payments.models import Payment, Transaction
from apps.orders.models import Order
from apps.orders.services import OrderService
from apps.users.tests.factories import UserFactory
from apps.products.tests.factories import ProductFactory, ProductVariantFactory
from apps.addresses.tests.factories import AddressFactory
from apps.cart.services import CartService


@pytest.fixture
def order_ready(db):
    user = UserFactory()
    address = AddressFactory(user=user)
    product = ProductFactory(price=Decimal('80000'))
    variant = ProductVariantFactory(product=product, stock=5)
    CartService.add_item(user, product.id, 1, variant.id)
    order = OrderService.create_from_cart(user, address.id)
    return user, order


@pytest.mark.django_db
class TestPaymentService:

    def test_create_payment_intent_success(self, order_ready):
        user, order = order_ready

        mock_result = MagicMock()
        mock_result.payment_intent_id = 'pi_test_123'
        mock_result.client_secret = 'pi_test_123_secret'
        mock_result.status = 'requires_payment_method'

        with patch('apps.payments.processors.stripe_adapter.stripe.PaymentIntent.create', return_value=MagicMock(
            id='pi_test_123',
            client_secret='pi_test_123_secret',
            status='requires_payment_method',
        )):
            result = PaymentService.create_payment_intent(user, order.id)

        assert result['payment_intent_id'] == 'pi_test_123'
        assert result['client_secret'] == 'pi_test_123_secret'
        assert 'publishable_key' in result

        payment = Payment.objects.get(order=order)
        assert payment.status == Payment.Status.PROCESSING
        assert payment.payment_intent_id == 'pi_test_123'

    def test_create_payment_intent_creates_transaction(self, order_ready):
        user, order = order_ready

        with patch('apps.payments.processors.stripe_adapter.stripe.PaymentIntent.create', return_value=MagicMock(
            id='pi_test_456',
            client_secret='secret_456',
            status='requires_payment_method',
        )):
            PaymentService.create_payment_intent(user, order.id)

        payment = Payment.objects.get(order=order)
        assert payment.transactions.filter(event_type=Transaction.EventType.CREATED).exists()

    def test_cannot_pay_already_approved_order(self, order_ready):
        from rest_framework.exceptions import ValidationError
        user, order = order_ready

        with patch('apps.payments.processors.stripe_adapter.stripe.PaymentIntent.create', return_value=MagicMock(
            id='pi_test_789', client_secret='secret_789', status='succeeded',
        )):
            PaymentService.create_payment_intent(user, order.id)

        # Marcar como aprobado
        payment = Payment.objects.get(order=order)
        payment.status = Payment.Status.APPROVED
        payment.save()

        with pytest.raises(ValidationError):
            PaymentService.create_payment_intent(user, order.id)


@pytest.mark.django_db
class TestWebhookProcessing:

    def test_webhook_succeeded_updates_order_and_payment(self, order_ready):
        user, order = order_ready

        with patch('apps.payments.processors.stripe_adapter.stripe.PaymentIntent.create', return_value=MagicMock(
            id='pi_webhook_test', client_secret='secret', status='requires_payment_method',
        )):
            PaymentService.create_payment_intent(user, order.id)

        mock_event = {
            'type': 'payment_intent.succeeded',
            'data': {'object': {'id': 'pi_webhook_test', 'status': 'succeeded'}},
        }

        with patch('apps.payments.processors.stripe_adapter.stripe.Webhook.construct_event') as mock_webhook:
            mock_event_obj = MagicMock()
            mock_event_obj.type = 'payment_intent.succeeded'
            mock_event_obj.data.object.id = 'pi_webhook_test'
            mock_event_obj.data.object.status = 'succeeded'
            mock_webhook.return_value = mock_event_obj

            PaymentService.process_webhook(b'payload', 'sig_test')

        payment = Payment.objects.get(payment_intent_id='pi_webhook_test')
        order.refresh_from_db()
        assert payment.status == Payment.Status.APPROVED
        assert order.status == Order.Status.PAYMENT_APPROVED

    def test_webhook_failed_updates_order_to_rejected(self, order_ready):
        user, order = order_ready

        with patch('apps.payments.processors.stripe_adapter.stripe.PaymentIntent.create', return_value=MagicMock(
            id='pi_fail_test', client_secret='secret', status='requires_payment_method',
        )):
            PaymentService.create_payment_intent(user, order.id)

        with patch('apps.payments.processors.stripe_adapter.stripe.Webhook.construct_event') as mock_webhook:
            mock_event_obj = MagicMock()
            mock_event_obj.type = 'payment_intent.payment_failed'
            mock_event_obj.data.object.id = 'pi_fail_test'
            mock_event_obj.data.object.status = 'requires_payment_method'
            mock_webhook.return_value = mock_event_obj

            PaymentService.process_webhook(b'payload', 'sig_test')

        payment = Payment.objects.get(payment_intent_id='pi_fail_test')
        order.refresh_from_db()
        assert payment.status == Payment.Status.REJECTED
        assert order.status == Order.Status.PAYMENT_REJECTED

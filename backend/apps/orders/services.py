from decimal import Decimal
from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound

from .models import Order, OrderItem
from .exceptions import EmptyCartError, InsufficientStockError, InvalidCouponError
from apps.cart.services import CartService
from apps.addresses.models import Address
from apps.coupons.services import CouponService
from apps.users.models import User


class OrderService:

    @staticmethod
    @transaction.atomic
    def create_from_cart(
        user: User,
        address_id: int,
        coupon_code: str = None,
        notes: str = '',
        payment_provider: str = 'stripe'
    ) -> Order:
        # 1. Obtener carrito
        cart = CartService.get_or_create_cart(user)
        if not cart.items.exists():
            raise EmptyCartError('El carrito está vacío.')

        # 2. Validar stock (con select_for_update para evitar race conditions)
        stock_errors = CartService.validate_stock_for_checkout(cart)
        if stock_errors:
            raise ValidationError({'stock_errors': stock_errors})

        # 3. Validar dirección
        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            raise NotFound('Dirección no encontrada.')

        # 4. Calcular subtotal
        subtotal = cart.subtotal

        # 5. Aplicar cupón si existe
        discount_amount = Decimal('0.00')
        coupon = None
        if coupon_code:
            coupon = CouponService.validate_and_get(coupon_code, subtotal)
            discount_amount = CouponService.apply(coupon, subtotal)

        total = subtotal - discount_amount

        # 6. Crear la orden
        order = Order.objects.create(
            user=user,
            address=address,
            coupon=coupon,
            status=Order.Status.PAYMENT_PENDING,
            subtotal=subtotal,
            discount_amount=discount_amount,
            total=total,
            notes=notes,
        )

        # 7. Crear items de la orden y descontar stock
        for item in cart.items.select_related('product', 'variant').all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                product_name=item.product.name,
                variant_detail=str(item.variant) if item.variant else '',
                unit_price=item.unit_price,
                quantity=item.quantity,
            )
            # Descontar stock de la variante
            if item.variant:
                item.variant.__class__.objects.filter(pk=item.variant.pk).update(
                    stock=item.variant.stock - item.quantity
                )

        # 8. Marcar cupón como usado
        if coupon:
            CouponService.mark_used(coupon)

        # 9. Limpiar carrito
        CartService.clear_cart(user)

        return order

    @staticmethod
    def get_user_orders(user: User):
        return Order.objects.filter(user=user).prefetch_related('items').select_related('address').order_by('-created_at')

    @staticmethod
    def get_order_detail(user: User, order_id: int) -> Order:
        try:
            return Order.objects.prefetch_related('items').select_related('address', 'payment').get(
                id=order_id, user=user
            )
        except Order.DoesNotExist:
            raise NotFound('Pedido no encontrado.')

    @staticmethod
    def update_status(order: Order, new_status: str) -> Order:
        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
        return order

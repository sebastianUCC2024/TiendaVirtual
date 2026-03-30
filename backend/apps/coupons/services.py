from decimal import Decimal
from rest_framework.exceptions import ValidationError, NotFound
from .models import Coupon


class CouponService:

    @staticmethod
    def validate_and_get(code: str, order_amount: Decimal) -> Coupon:
        try:
            coupon = Coupon.objects.get(code=code.upper())
        except Coupon.DoesNotExist:
            raise NotFound('Cupón no encontrado.')

        if not coupon.is_valid():
            raise ValidationError('El cupón no es válido o ha expirado.')

        if order_amount < coupon.min_order_amount:
            raise ValidationError(
                f'El monto mínimo para este cupón es ${coupon.min_order_amount}.'
            )
        return coupon

    @staticmethod
    def apply(coupon: Coupon, amount: Decimal) -> Decimal:
        """Retorna el monto de descuento a aplicar."""
        return coupon.calculate_discount(amount)

    @staticmethod
    def mark_used(coupon: Coupon) -> None:
        Coupon.objects.filter(pk=coupon.pk).update(used_count=coupon.used_count + 1)

import pytest
from decimal import Decimal
from django.utils import timezone
from apps.coupons.models import Coupon
from .factories import CouponFactory


@pytest.mark.django_db
class TestCouponModel:

    def test_valid_coupon(self):
        coupon = CouponFactory()
        assert coupon.is_valid() is True

    def test_inactive_coupon_is_invalid(self):
        coupon = CouponFactory(is_active=False)
        assert coupon.is_valid() is False

    def test_expired_coupon_is_invalid(self):
        coupon = CouponFactory(
            valid_until=timezone.now() - timezone.timedelta(days=1)
        )
        assert coupon.is_valid() is False

    def test_max_uses_reached_is_invalid(self):
        coupon = CouponFactory(max_uses=5, used_count=5)
        assert coupon.is_valid() is False

    def test_percentage_discount_calculation(self):
        coupon = CouponFactory(discount_type=Coupon.DiscountType.PERCENTAGE, discount_value=10)
        discount = coupon.calculate_discount(Decimal('100000'))
        assert discount == Decimal('10000.00')

    def test_fixed_discount_calculation(self):
        coupon = CouponFactory(discount_type=Coupon.DiscountType.FIXED, discount_value=20000)
        discount = coupon.calculate_discount(Decimal('100000'))
        assert discount == Decimal('20000')

    def test_fixed_discount_cannot_exceed_order_amount(self):
        coupon = CouponFactory(discount_type=Coupon.DiscountType.FIXED, discount_value=200000)
        discount = coupon.calculate_discount(Decimal('50000'))
        assert discount == Decimal('50000')

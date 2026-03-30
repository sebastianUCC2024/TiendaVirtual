import factory
from django.utils import timezone
from apps.coupons.models import Coupon


class CouponFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Coupon

    code = factory.Sequence(lambda n: f'PROMO{n}')
    discount_type = Coupon.DiscountType.PERCENTAGE
    discount_value = 10
    min_order_amount = 0
    valid_from = factory.LazyFunction(timezone.now)
    valid_until = factory.LazyFunction(lambda: timezone.now() + timezone.timedelta(days=30))
    is_active = True

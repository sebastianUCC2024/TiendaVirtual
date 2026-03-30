import pytest
from decimal import Decimal
from apps.orders.services import OrderService
from apps.orders.models import Order
from apps.orders.exceptions import EmptyCartError
from apps.cart.services import CartService
from apps.users.tests.factories import UserFactory
from apps.products.tests.factories import ProductFactory, ProductVariantFactory
from apps.addresses.tests.factories import AddressFactory
from apps.coupons.tests.factories import CouponFactory


@pytest.mark.django_db
class TestOrderService:

    def setup_method(self):
        self.user = UserFactory()
        self.address = AddressFactory(user=self.user)
        self.product = ProductFactory(price=Decimal('50000'))
        self.variant = ProductVariantFactory(product=self.product, stock=10)

    def _fill_cart(self, quantity=2):
        CartService.add_item(self.user, self.product.id, quantity, self.variant.id)

    def test_create_order_from_cart(self):
        self._fill_cart(2)
        order = OrderService.create_from_cart(self.user, self.address.id)
        assert order.pk is not None
        assert order.status == Order.Status.PAYMENT_PENDING
        assert order.items.count() == 1
        assert order.total == Decimal('100000')

    def test_order_clears_cart_after_creation(self):
        self._fill_cart(2)
        OrderService.create_from_cart(self.user, self.address.id)
        cart = CartService.get_or_create_cart(self.user)
        assert cart.items.count() == 0

    def test_order_decrements_stock(self):
        self._fill_cart(3)
        OrderService.create_from_cart(self.user, self.address.id)
        self.variant.refresh_from_db()
        assert self.variant.stock == 7

    def test_order_snapshots_product_name(self):
        self._fill_cart(1)
        order = OrderService.create_from_cart(self.user, self.address.id)
        item = order.items.first()
        assert item.product_name == self.product.name

    def test_empty_cart_raises_error(self):
        with pytest.raises(EmptyCartError):
            OrderService.create_from_cart(self.user, self.address.id)

    def test_order_with_percentage_coupon(self):
        self._fill_cart(2)  # subtotal = 100000
        coupon = CouponFactory(discount_type='percentage', discount_value=10)
        order = OrderService.create_from_cart(self.user, self.address.id, coupon_code=coupon.code)
        assert order.discount_amount == Decimal('10000.00')
        assert order.total == Decimal('90000.00')

    def test_order_with_fixed_coupon(self):
        self._fill_cart(2)  # subtotal = 100000
        coupon = CouponFactory(discount_type='fixed', discount_value=Decimal('15000'))
        order = OrderService.create_from_cart(self.user, self.address.id, coupon_code=coupon.code)
        assert order.discount_amount == Decimal('15000')
        assert order.total == Decimal('85000')

    def test_coupon_used_count_increments(self):
        self._fill_cart(1)
        coupon = CouponFactory()
        OrderService.create_from_cart(self.user, self.address.id, coupon_code=coupon.code)
        coupon.refresh_from_db()
        assert coupon.used_count == 1

    def test_update_order_status(self):
        self._fill_cart(1)
        order = OrderService.create_from_cart(self.user, self.address.id)
        updated = OrderService.update_status(order, Order.Status.PREPARING)
        assert updated.status == Order.Status.PREPARING

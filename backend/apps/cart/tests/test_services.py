import pytest
from apps.cart.services import CartService
from apps.cart.exceptions import InsufficientStockError
from apps.users.tests.factories import UserFactory
from apps.products.tests.factories import ProductFactory, ProductVariantFactory


@pytest.mark.django_db
class TestCartService:

    def setup_method(self):
        self.user = UserFactory()
        self.product = ProductFactory()
        self.variant = ProductVariantFactory(product=self.product, stock=5)

    def test_get_or_create_cart(self):
        cart = CartService.get_or_create_cart(self.user)
        assert cart.user == self.user
        # Segunda llamada retorna el mismo carrito
        cart2 = CartService.get_or_create_cart(self.user)
        assert cart.id == cart2.id

    def test_add_item_with_variant(self):
        CartService.add_item(self.user, self.product.id, 2, self.variant.id)
        cart = CartService.get_or_create_cart(self.user)
        assert cart.items.count() == 1
        assert cart.items.first().quantity == 2

    def test_add_same_item_accumulates_quantity(self):
        CartService.add_item(self.user, self.product.id, 2, self.variant.id)
        CartService.add_item(self.user, self.product.id, 1, self.variant.id)
        cart = CartService.get_or_create_cart(self.user)
        assert cart.items.first().quantity == 3

    def test_add_item_exceeding_stock_raises_error(self):
        with pytest.raises(InsufficientStockError):
            CartService.add_item(self.user, self.product.id, 10, self.variant.id)

    def test_update_item_quantity(self):
        CartService.add_item(self.user, self.product.id, 1, self.variant.id)
        cart = CartService.get_or_create_cart(self.user)
        item = cart.items.first()
        CartService.update_item(self.user, item.id, 3)
        item.refresh_from_db()
        assert item.quantity == 3

    def test_remove_item(self):
        CartService.add_item(self.user, self.product.id, 1, self.variant.id)
        cart = CartService.get_or_create_cart(self.user)
        item = cart.items.first()
        CartService.remove_item(self.user, item.id)
        assert cart.items.count() == 0

    def test_clear_cart(self):
        CartService.add_item(self.user, self.product.id, 1, self.variant.id)
        CartService.clear_cart(self.user)
        cart = CartService.get_or_create_cart(self.user)
        assert cart.items.count() == 0

    def test_validate_stock_for_checkout_passes(self):
        CartService.add_item(self.user, self.product.id, 2, self.variant.id)
        cart = CartService.get_or_create_cart(self.user)
        errors = CartService.validate_stock_for_checkout(cart)
        assert errors == []

    def test_validate_stock_for_checkout_fails_when_stock_reduced(self):
        CartService.add_item(self.user, self.product.id, 3, self.variant.id)
        # Reducir stock manualmente
        self.variant.stock = 1
        self.variant.save()
        cart = CartService.get_or_create_cart(self.user)
        errors = CartService.validate_stock_for_checkout(cart)
        assert len(errors) == 1
        assert errors[0]['product'] == self.product.name

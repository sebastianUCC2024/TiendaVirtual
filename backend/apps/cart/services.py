from django.db import transaction
from rest_framework.exceptions import NotFound, ValidationError
from .models import Cart, CartItem
from .exceptions import InsufficientStockError, ProductNotAvailableError
from apps.products.models import Product, ProductVariant
from apps.users.models import User


class CartService:

    @staticmethod
    def get_or_create_cart(user: User) -> Cart:
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    @transaction.atomic
    def add_item(user: User, product_id: int, quantity: int, variant_id: int = None) -> CartItem:
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            raise NotFound('Producto no encontrado o no disponible.')

        variant = None
        if variant_id:
            try:
                variant = ProductVariant.objects.get(id=variant_id, product=product, is_active=True)
            except ProductVariant.DoesNotExist:
                raise NotFound('Variante no encontrada.')

        cart = CartService.get_or_create_cart(user)

        # Si ya existe el item, sumar cantidad
        existing = CartItem.objects.filter(cart=cart, product=product, variant=variant).first()
        current_qty = existing.quantity if existing else 0

        if variant and (current_qty + quantity) > variant.stock:
            raise InsufficientStockError(product.name, variant.stock)

        if existing:
            existing.quantity += quantity
            existing.save()
            return existing

        return CartItem.objects.create(cart=cart, product=product, variant=variant, quantity=quantity)

    @staticmethod
    def update_item(user: User, item_id: int, quantity: int) -> CartItem:
        try:
            item = CartItem.objects.select_related('variant').get(id=item_id, cart__user=user)
        except CartItem.DoesNotExist:
            raise NotFound('Item no encontrado en el carrito.')

        if item.variant and quantity > item.variant.stock:
            raise InsufficientStockError(item.product.name, item.variant.stock)

        item.quantity = quantity
        item.save()
        return item

    @staticmethod
    def remove_item(user: User, item_id: int) -> None:
        deleted, _ = CartItem.objects.filter(id=item_id, cart__user=user).delete()
        if not deleted:
            raise NotFound('Item no encontrado en el carrito.')

    @staticmethod
    def clear_cart(user: User) -> None:
        cart = CartService.get_or_create_cart(user)
        cart.items.all().delete()

    @staticmethod
    def validate_stock_for_checkout(cart: Cart) -> list[dict]:
        """
        Valida que todos los items del carrito tengan stock suficiente.
        Retorna lista de errores si los hay.
        """
        errors = []
        for item in cart.items.select_related('product', 'variant').all():
            if item.variant:
                if item.quantity > item.variant.stock:
                    errors.append({
                        'product': item.product.name,
                        'variant': str(item.variant),
                        'requested': item.quantity,
                        'available': item.variant.stock,
                    })
            elif not item.product.is_active:
                errors.append({'product': item.product.name, 'error': 'Producto no disponible.'})
        return errors

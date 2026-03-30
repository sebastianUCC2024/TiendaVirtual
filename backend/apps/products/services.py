from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound
from .models import Product, Category, ProductVariant, ProductImage


class CategoryService:

    @staticmethod
    def get_active_tree():
        return Category.objects.filter(is_active=True, parent=None).prefetch_related('subcategories').order_by('name')

    @staticmethod
    def create(data: dict) -> Category:
        return Category.objects.create(**data)

    @staticmethod
    def update(instance: Category, data: dict) -> Category:
        for attr, value in data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    @staticmethod
    def soft_delete(instance: Category) -> None:
        instance.is_active = False
        instance.save()


class ProductService:

    @staticmethod
    def get_active_products(filters: dict = None):
        qs = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'variants')
        if filters:
            if filters.get('category'):
                qs = qs.filter(category__slug=filters['category'])
            if filters.get('is_featured'):
                qs = qs.filter(is_featured=True)
        return qs

    @staticmethod
    @transaction.atomic
    def create_product(data: dict) -> Product:
        variants_data = data.pop('variants', [])
        product = Product.objects.create(**data)
        for v in variants_data:
            ProductVariant.objects.create(product=product, **v)
        return product

    @staticmethod
    @transaction.atomic
    def update_product(instance: Product, data: dict) -> Product:
        for attr, value in data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    @staticmethod
    def add_image(product: Product, image_file, alt_text: str = '', is_primary: bool = False) -> ProductImage:
        if is_primary:
            product.images.filter(is_primary=True).update(is_primary=False)
        return ProductImage.objects.create(
            product=product, image=image_file,
            alt_text=alt_text, is_primary=is_primary
        )

    @staticmethod
    def update_variant_stock(variant_id: int, quantity: int) -> ProductVariant:
        try:
            variant = ProductVariant.objects.select_for_update().get(id=variant_id)
        except ProductVariant.DoesNotExist:
            raise NotFound('Variante no encontrada.')
        if variant.stock + quantity < 0:
            raise ValidationError('Stock no puede ser negativo.')
        variant.stock += quantity
        variant.save()
        return variant

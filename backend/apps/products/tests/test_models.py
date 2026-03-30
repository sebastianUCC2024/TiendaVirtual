import pytest
from apps.products.models import Product
from .factories import CategoryFactory, ProductFactory, ProductVariantFactory


@pytest.mark.django_db
class TestCategoryModel:

    def test_slug_auto_generated(self):
        cat = CategoryFactory(name='Brasieres Push Up')
        assert cat.slug == 'brasieres-push-up'

    def test_subcategory_relation(self):
        parent = CategoryFactory(name='Ropa Interior')
        child = CategoryFactory(name='Brasieres', parent=parent)
        assert child.parent == parent
        assert parent.subcategories.count() == 1


@pytest.mark.django_db
class TestProductModel:

    def test_slug_auto_generated(self):
        product = ProductFactory(name='Brasier Deportivo')
        assert product.slug == 'brasier-deportivo'

    def test_effective_price_returns_sale_price_when_set(self):
        product = ProductFactory(price=100000, sale_price=80000)
        assert product.effective_price == 80000

    def test_effective_price_returns_price_when_no_sale(self):
        product = ProductFactory(price=100000, sale_price=None)
        assert product.effective_price == 100000

    def test_sku_is_unique(self):
        ProductFactory(sku='UNIQUE-001')
        with pytest.raises(Exception):
            ProductFactory(sku='UNIQUE-001')


@pytest.mark.django_db
class TestProductVariantModel:

    def test_variant_str(self):
        variant = ProductVariantFactory(size='M', color='Negro')
        assert 'M' in str(variant)
        assert 'Negro' in str(variant)

    def test_unique_together_size_color(self):
        product = ProductFactory()
        ProductVariantFactory(product=product, size='M', color='Negro', sku='V001')
        with pytest.raises(Exception):
            ProductVariantFactory(product=product, size='M', color='Negro', sku='V002')

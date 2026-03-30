import factory
from apps.products.models import Category, Product, ProductVariant


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f'Categoría {n}')
    is_active = True


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f'Brasier {n}')
    sku = factory.Sequence(lambda n: f'SKU-{n:04d}')
    price = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    category = factory.SubFactory(CategoryFactory)
    is_active = True


class ProductVariantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductVariant

    product = factory.SubFactory(ProductFactory)
    size = ProductVariant.Size.M
    color = 'Negro'
    sku = factory.Sequence(lambda n: f'VAR-{n:04d}')
    stock = 10
    is_active = True

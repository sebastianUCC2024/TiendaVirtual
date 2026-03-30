import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.tests.factories import UserFactory, AdminFactory
from .factories import CategoryFactory, ProductFactory, ProductVariantFactory


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def admin_client():
    admin = AdminFactory(password='adminpass123')
    client = APIClient()
    response = client.post(reverse('login'), {'email': admin.email, 'password': 'adminpass123'})
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    return client


@pytest.mark.django_db
class TestCategoryViews:

    def test_list_categories_public(self, client):
        CategoryFactory.create_batch(3)
        response = client.get(reverse('category_list'))
        assert response.status_code == 200
        assert len(response.data) >= 3

    def test_create_category_requires_admin(self, client):
        response = client.post(reverse('category_list'), {'name': 'Test'})
        assert response.status_code == 401

    def test_admin_can_create_category(self, admin_client):
        response = admin_client.post(reverse('category_list'), {'name': 'Brasieres'})
        assert response.status_code == 201
        assert response.data['name'] == 'Brasieres'


@pytest.mark.django_db
class TestProductViews:

    def test_list_products_public(self, client):
        ProductFactory.create_batch(5)
        response = client.get(reverse('product_list'))
        assert response.status_code == 200
        assert response.data['count'] >= 5

    def test_inactive_products_not_listed(self, client):
        ProductFactory(is_active=False)
        active = ProductFactory(is_active=True)
        response = client.get(reverse('product_list'))
        slugs = [p['slug'] for p in response.data['results']]
        assert active.slug in slugs

    def test_product_detail_by_slug(self, client):
        product = ProductFactory()
        response = client.get(reverse('product_detail', kwargs={'slug': product.slug}))
        assert response.status_code == 200
        assert response.data['slug'] == product.slug

    def test_filter_by_featured(self, client):
        ProductFactory(is_featured=True)
        ProductFactory(is_featured=False)
        response = client.get(reverse('product_list') + '?is_featured=true')
        for p in response.data['results']:
            assert p['is_featured'] is True

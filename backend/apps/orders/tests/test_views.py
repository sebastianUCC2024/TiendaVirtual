import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.tests.factories import UserFactory, AdminFactory
from apps.products.tests.factories import ProductFactory, ProductVariantFactory
from apps.addresses.tests.factories import AddressFactory
from apps.cart.services import CartService


@pytest.fixture
def auth_client():
    user = UserFactory(password='testpass123')
    client = APIClient()
    response = client.post(reverse('login'), {'email': user.email, 'password': 'testpass123'})
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    client.user = user
    return client


@pytest.fixture
def admin_client():
    admin = AdminFactory(password='adminpass123')
    client = APIClient()
    response = client.post(reverse('login'), {'email': admin.email, 'password': 'adminpass123'})
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    return client


@pytest.mark.django_db
class TestCheckoutView:

    def setup_method(self):
        self.product = ProductFactory(price=Decimal('50000'))
        self.variant = ProductVariantFactory(product=self.product, stock=10)

    def test_checkout_creates_order(self, auth_client):
        address = AddressFactory(user=auth_client.user)
        CartService.add_item(auth_client.user, self.product.id, 2, self.variant.id)
        response = auth_client.post(reverse('checkout'), {'address_id': address.id})
        assert response.status_code == 201
        assert response.data['status'] == 'payment_pending'
        assert response.data['total'] == '100000.00'

    def test_checkout_empty_cart_returns_400(self, auth_client):
        address = AddressFactory(user=auth_client.user)
        response = auth_client.post(reverse('checkout'), {'address_id': address.id})
        assert response.status_code == 400

    def test_checkout_requires_auth(self):
        client = APIClient()
        response = client.post(reverse('checkout'), {})
        assert response.status_code == 401

    def test_list_orders(self, auth_client):
        address = AddressFactory(user=auth_client.user)
        CartService.add_item(auth_client.user, self.product.id, 1, self.variant.id)
        auth_client.post(reverse('checkout'), {'address_id': address.id})
        response = auth_client.get(reverse('order_list'))
        assert response.status_code == 200
        assert response.data['count'] == 1


@pytest.mark.django_db
class TestAdminOrderViews:

    def test_admin_can_list_all_orders(self, admin_client):
        response = admin_client.get(reverse('admin_order_list'))
        assert response.status_code == 200

    def test_client_cannot_access_admin_orders(self, auth_client):
        response = auth_client.get(reverse('admin_order_list'))
        assert response.status_code == 403

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User
from .factories import UserFactory


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client():
    user = UserFactory(password='testpass123')
    client = APIClient()
    response = client.post(reverse('login'), {'email': user.email, 'password': 'testpass123'})
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    client.user = user
    return client


@pytest.mark.django_db
class TestRegisterView:

    def test_register_success(self, client):
        data = {
            'email': 'nueva@test.com',
            'username': 'nueva',
            'first_name': 'Ana',
            'last_name': 'García',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = client.post(reverse('register'), data)
        assert response.status_code == 201
        assert User.objects.filter(email='nueva@test.com').exists()

    def test_register_passwords_mismatch(self, client):
        data = {
            'email': 'test@test.com', 'username': 'test',
            'password': 'Pass123!', 'password2': 'Different123!',
        }
        response = client.post(reverse('register'), data)
        assert response.status_code == 400

    def test_register_duplicate_email(self, client):
        UserFactory(email='dup@test.com')
        data = {
            'email': 'dup@test.com', 'username': 'dup2',
            'password': 'Pass123!', 'password2': 'Pass123!',
        }
        response = client.post(reverse('register'), data)
        assert response.status_code == 400


@pytest.mark.django_db
class TestLoginView:

    def test_login_success(self, client):
        UserFactory(email='login@test.com', password='testpass123')
        response = client.post(reverse('login'), {'email': 'login@test.com', 'password': 'testpass123'})
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_wrong_password(self, client):
        UserFactory(email='login2@test.com', password='correct')
        response = client.post(reverse('login'), {'email': 'login2@test.com', 'password': 'wrong'})
        assert response.status_code == 401


@pytest.mark.django_db
class TestMeView:

    def test_get_profile(self, auth_client):
        response = auth_client.get(reverse('me'))
        assert response.status_code == 200
        assert response.data['email'] == auth_client.user.email

    def test_unauthenticated_returns_401(self, client):
        response = client.get(reverse('me'))
        assert response.status_code == 401

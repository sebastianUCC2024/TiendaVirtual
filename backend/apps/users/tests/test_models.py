import pytest
from apps.users.models import User
from .factories import UserFactory, AdminFactory


@pytest.mark.django_db
class TestUserModel:

    def test_create_client_user(self):
        user = UserFactory()
        assert user.pk is not None
        assert user.role == User.Role.CLIENT
        assert user.is_admin is False

    def test_create_admin_user(self):
        admin = AdminFactory()
        assert admin.role == User.Role.ADMIN
        assert admin.is_admin is True

    def test_email_is_unique(self):
        UserFactory(email='same@test.com')
        with pytest.raises(Exception):
            UserFactory(email='same@test.com')

    def test_password_is_hashed(self):
        user = UserFactory(password='plainpassword')
        assert user.password != 'plainpassword'
        assert user.check_password('plainpassword')

    def test_str_returns_email(self):
        user = UserFactory(email='test@example.com')
        assert str(user) == 'test@example.com'

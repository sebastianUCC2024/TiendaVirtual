import factory
from apps.users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'user{n}@test.com')
    username = factory.Sequence(lambda n: f'user{n}')
    first_name = 'Test'
    last_name = 'User'
    role = User.Role.CLIENT
    is_active = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop('password', 'testpass123')
        user = model_class(**kwargs)
        user.set_password(password)
        user.save()
        return user


class AdminFactory(UserFactory):
    role = User.Role.ADMIN
    email = factory.Sequence(lambda n: f'admin{n}@test.com')
    username = factory.Sequence(lambda n: f'admin{n}')

import factory
from apps.addresses.models import Address
from apps.users.tests.factories import UserFactory


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

    user = factory.SubFactory(UserFactory)
    full_name = 'Ana García'
    phone = '3001234567'
    address_line = 'Calle 123 # 45-67'
    city = 'Bogotá'
    department = 'Cundinamarca'
    country = 'Colombia'
    is_default = False

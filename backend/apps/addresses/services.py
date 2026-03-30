from rest_framework.exceptions import PermissionDenied, NotFound
from .models import Address
from apps.users.models import User


class AddressService:

    @staticmethod
    def get_user_addresses(user: User):
        return Address.objects.filter(user=user).order_by('-is_default', '-created_at')

    @staticmethod
    def set_default(user: User, address_id: int) -> Address:
        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            raise NotFound('Dirección no encontrada.')
        Address.objects.filter(user=user, is_default=True).update(is_default=False)
        address.is_default = True
        address.save()
        return address

    @staticmethod
    def delete(user: User, address_id: int) -> None:
        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            raise NotFound('Dirección no encontrada.')
        address.delete()

from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from .models import User


class UserService:

    @staticmethod
    def register(validated_data: dict) -> User:
        """Crea un nuevo usuario cliente."""
        if User.objects.filter(email=validated_data['email']).exists():
            raise ValidationError({'email': 'Ya existe una cuenta con este correo.'})
        validated_data.pop('password2', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def change_password(user: User, old_password: str, new_password: str) -> None:
        if not user.check_password(old_password):
            raise ValidationError({'old_password': 'Contraseña actual incorrecta.'})
        user.set_password(new_password)
        user.save()

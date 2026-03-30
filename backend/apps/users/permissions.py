from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """Solo usuarios con rol admin pueden acceder."""
    message = 'Se requieren permisos de administrador.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsOwnerOrAdmin(BasePermission):
    """El usuario puede acceder solo a sus propios recursos, o si es admin."""
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        return obj.user == request.user

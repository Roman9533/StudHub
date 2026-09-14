from rest_framework import permissions
from .models import User


class IsModeratorOrAuthorReadOnly(permissions.BasePermission):
    """
    Доступ на изменение/удаление имеют только авторы или модераторы.
    Остальные пользователи имеют доступ только на чтение.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False
            
        return (
            obj.author == request.user or 
            request.user.role == User.Roles.MODERATOR or 
            request.user.is_staff
        )

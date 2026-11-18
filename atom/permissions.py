from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает полный доступ владельцу объекта.
    Остальным — только чтение (если привычка публичная).
    """
    def has_object_permission(self, request, view, obj):
        # Разрешения на чтение (GET, HEAD, OPTIONS) разрешены всегда
        if request.method in permissions.SAFE_METHODS:
            # Если привычка не публичная, читать может только владелец
            if not obj.is_published and obj.owner != request.user:
                return False
            return True

        # Разрешения на запись (PUT, PATCH, DELETE) только для владельца
        return obj.owner == request.user
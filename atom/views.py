from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import Habit
from .serializers import HabitSerializer
from .permissions import IsOwnerOrReadOnly


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()

    def get_permissions(self):
        """
        Настраиваем права в зависимости от действия.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Создавать, изменять и удалять может только авторизованный
            self.permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        else:
            # Смотреть могут все (но фильтрация queryset отсеет лишнее)
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_queryset(self):
        """
        Фильтрация привычек:
        - Авторизованный видит свои + публичные.
        - Неавторизованный видит только публичные.
        """
        user = self.request.user
        if user.is_authenticated:
            return Habit.objects.filter(owner=user) | Habit.objects.filter(is_published=True)
        return Habit.objects.filter(is_published=True)

    def perform_create(self, serializer):
        """
        При создании автоматически привязываем владельца.
        """
        serializer.save(owner=self.request.user)
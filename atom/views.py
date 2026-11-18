from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response

from atom.models import Habit
from atom.serializers import HabitSerializer
from atom.permissions import IsOwnerOrReadOnly


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()

    def get_permissions(self):
        """
        Настраиваем права в зависимости от действия.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
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
            return Habit.objects.filter(owner=user) | Habit.objects.filter(
                is_published=True
            )
        return Habit.objects.filter(is_published=True)

    def perform_create(self, serializer):
        """
        При создании автоматически привязываем владельца.
        """
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def public(self, request):
        """Эндпоинт для просмотра только публичных привычек"""
        public_habits = Habit.objects.filter(is_published=True)
        page = self.paginate_queryset(public_habits)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(public_habits, many=True)
        return Response(serializer.data)

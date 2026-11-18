from rest_framework import serializers
from atom.models import Habit
from django.core.exceptions import ValidationError as DjangoValidationError


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("owner",)

    def validate(self, attrs):
        # Создаем временный экземпляр модели с данными из запроса
        instance = Habit(**attrs)

        # Явная проверка времени (для надежности)
        time_to_action = attrs.get("time_to_action")
        if time_to_action and time_to_action.total_seconds() > 120:
            raise serializers.ValidationError(
                {"time_to_action": "Время выполнения не должно превышать 120 секунд."}
            )

        # Если это обновление (PUT/PATCH), нужно подтянуть текущие данные
        if self.instance:
            for key, value in attrs.items():
                setattr(self.instance, key, value)
            instance = self.instance

        try:
            # Вызываем валидацию модели (clean и валидаторы полей)
            instance.full_clean()
        except DjangoValidationError as e:
            # Переводим ошибки Django в формат DRF
            raise serializers.ValidationError(e.message_dict)

        return attrs

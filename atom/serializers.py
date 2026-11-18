from rest_framework import serializers
from .models import Habit
from .validators import validate_last_completion
from django.core.exceptions import ValidationError as DjangoValidationError


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'
        read_only_fields = ('owner',)  # Владелец назначается автоматически

    def validate(self, attrs):
        # DRF вызывает этот метод перед сохранением.
        # Мы можем вызвать нашу модель с текущими данными, чтобы сработал метод clean()

        # Создаем временный экземпляр (не сохраняя в БД), чтобы проверить валидацию
        instance = Habit(**attrs)

        # Если это обновление (Update), нужно подтянуть текущие данные
        if self.instance:
            for key, value in attrs.items():
                setattr(self.instance, key, value)
            instance = self.instance

        try:
            instance.full_clean()  # Вызывает clean() и валидаторы полей
        except DjangoValidationError as e:
            # Преобразуем ошибки Django в ошибки DRF
            raise serializers.ValidationError(e.message_dict)

        return attrs
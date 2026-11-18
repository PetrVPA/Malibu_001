from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

from man.models import Gent
from .validators import validate_time_to_action, validate_period

NULLABLE = {'null': True, 'blank': True}


class Habit(models.Model):
    owner = models.ForeignKey(
        Gent, on_delete=models.CASCADE, **NULLABLE, verbose_name="Создатель"
    )
    place = models.CharField(max_length=100, verbose_name="Место")
    time = models.TimeField(default=timezone.now, verbose_name="Время выполнения")
    action = models.CharField(max_length=100, verbose_name="Действие")

    # Исправлено название поля
    related_habit = models.ForeignKey(
        to="self", on_delete=models.SET_NULL, **NULLABLE, verbose_name="Связанная привычка"
    )

    # Добавлено поле "Признак приятной привычки"
    is_pleasant = models.BooleanField(default=False, verbose_name="Признак приятной привычки")

    # Добавлено значение по умолчанию для периодичности
    period = models.PositiveIntegerField(default=1, verbose_name="Периодичность")
    reward = models.CharField(max_length=100, **NULLABLE, verbose_name="Вознаграждение")
    time_to_action = models.DurationField(
        default=timezone.timedelta(seconds=60), verbose_name="Время на выполнение"
    )
    is_published = models.BooleanField(default=True, verbose_name="Признак публичности")



    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["id"]

    def __str__(self):
        return f"{self.action} — {self.place} ({self.time})"

    def clean(self):
        super().clean()
        errors = {}

        # 1. Нельзя одновременно связанную привычку и вознаграждение
        if self.related_habit and self.reward:
            errors["related_habit"] = (
                "Нельзя одновременно указывать связанную привычку и вознаграждение."
            )

        # 2. Связанная привычка должна быть приятной
        if self.related_habit and not self.related_habit.is_pleasant:
            errors["related_habit"] = (
                "В связанные привычки могут попадать только приятные привычки."
            )

        # 3. У приятной привычки не может быть вознаграждения/связи
        if self.is_pleasant:
            if self.reward:
                errors["reward"] = (
                    "У приятной привычки не может быть вознаграждения."
                )
            if self.related_habit:
                errors["related_habit"] = (
                    "У приятной привычки не может быть связанной привычки."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Вызовем clean(), чтобы валидация срабатывала и при save()
        self.full_clean()
        super().save(*args, **kwargs)

class HabitCompletion(models.Model):
    habit = models.ForeignKey(
        Habit, on_delete=models.CASCADE, related_name="completions",
        verbose_name="Привычка",
    )
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Выполнено")




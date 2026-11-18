from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta


def validate_related_habit_and_reward(value, field_name, related_habit, reward):
    """Нельзя одновременно указать связанную привычку и вознаграждение."""
    if value and related_habit:
        raise ValidationError(
            _("Нельзя одновременно указывать связанную привычку и вознаграждение.")
        )


def validate_time_to_action(value):
    """Время выполнения не должно превышать 120 секунд."""
    if value and value.total_seconds() > 120:
        raise ValidationError(
            _("Время выполнения привычки не должно превышать 120 секунд.")
        )


def validate_related_habit_is_pleasant(value):
    """Связанная привычка должна иметь признак приятной."""
    if value and not value.is_pleasant:
        raise ValidationError(
            _("В связанные привычки могут попадать только приятные привычки.")
        )


def validate_pleasant_habit(value, is_pleasant, reward, related_habit):
    """У приятной привычки не может быть вознаграждения или связанной привычки."""
    if is_pleasant:
        if reward:
            raise ValidationError(
                _("У приятной привычки не может быть вознаграждения.")
            )
        if related_habit:
            raise ValidationError(
                _("У приятной привычки не может быть связанной привычки.")
            )


def validate_period(value):
    """Периодичность не должна быть реже 1 раза в 7 дней."""
    if value is not None and value > 7:
        raise ValidationError(
            _("Нельзя выполнять привычку реже, чем 1 раз в 7 дней.")
        )
    if value is not None and value < 1:
        raise ValidationError(
            _("Периодичность должна быть не менее 1 дня.")
        )


def validate_last_completion(habit):
    """
    Проверяет, не забросил ли пользователь привычку
    (не выполнял её более 7 дней).
    """
    last = habit.completions.order_by("-completed_at").first()

    # Если пользователь еще ни разу не выполнял привычку,
    # мы не можем применить это правило (нет истории).
    if not last:
        return

    if timezone.now() - last.completed_at > timedelta(days=7):
        raise ValidationError(
            _("Привычка не выполнялась более 7 дней. За одну неделю "
              "необходимо выполнить привычку хотя бы один раз.")
        )
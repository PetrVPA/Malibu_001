from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import timedelta
from atom.validators import (
    validate_period,
    validate_time_to_action,
    validate_related_habit_is_pleasant,
    validate_pleasant_habit,
    validate_last_completion,
)
from .models import Habit
from man.models import Gent


class ValidatorsTestCase(TestCase):
    def test_validate_period_too_long(self):
        """Нельзя реже 1 раза в 7 дней"""
        with self.assertRaises(ValidationError):
            validate_period(8)

    def test_validate_period_too_short(self):
        """Периодичность не может быть меньше 1"""
        with self.assertRaises(ValidationError):
            validate_period(0)

    def test_validate_time_to_action(self):
        """Время выполнения > 120 сек вызывает ошибку"""
        with self.assertRaises(ValidationError):
            validate_time_to_action(timedelta(seconds=121))

    def test_validate_related_habit_is_pleasant(self):
        """Связанная привычка должна быть приятной"""
        user = Gent.objects.create_user(username="test", password="123")
        habit = Habit.objects.create(
            owner=user, place="Дом", time="12:00:00", action="Тест", is_pleasant=False
        )
        with self.assertRaises(ValidationError):
            validate_related_habit_is_pleasant(habit)

    def test_validate_pleasant_habit_with_reward(self):
        """У приятной привычки не может быть вознаграждения"""
        with self.assertRaises(ValidationError):
            validate_pleasant_habit(
                None, is_pleasant=True, reward="Конфета", related_habit=None
            )

    def test_validate_pleasant_habit_with_related(self):
        """У приятной привычки не может быть связанной привычки"""
        with self.assertRaises(ValidationError):
            validate_pleasant_habit(
                None, is_pleasant=True, reward=None, related_habit=True
            )

    def test_validate_last_completion_no_history(self):
        """Если нет истории выполнений, валидатор молчит (не падает)"""
        user = Gent.objects.create_user(username="test2", password="123")
        habit = Habit.objects.create(
            owner=user, place="Дом", time="12:00:00", action="Тест"
        )
        try:
            validate_last_completion(habit)  # Не должно быть ошибки
        except ValidationError:
            self.fail("Валидатор не должен падать без истории выполнений")

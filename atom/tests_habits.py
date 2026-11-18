from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from atom.models import Habit
from datetime import timedelta

User = get_user_model()


class HabitAPITestCase(APITestCase):
    def setUp(self):
        """Создаем двух пользователей для тестов прав доступа"""
        self.user1 = User.objects.create_user(
            username="user1", password="pass123", chat_id="111"
        )
        self.user2 = User.objects.create_user(
            username="user2", password="pass123", chat_id="222"
        )

        # Создаем привычку для user1
        self.habit = Habit.objects.create(
            owner=self.user1,
            place="Дом",
            time="12:00:00",
            action="Отжаться",
            period=1,
            time_to_action=timedelta(seconds=60),
            is_published=True,
        )

        self.list_url = reverse("habit-list")  # name='habit-list' из DefaultRouter

    def test_create_habit_authorized(self):
        """Авторизованный пользователь может создать привычку"""
        self.client.force_authenticate(user=self.user1)
        data = {
            "place": "Спортзал",
            "time": "18:00:00",
            "action": "Приседания",
            "period": 1,
            "time_to_action": "00:01:00",
            "is_published": False,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Проверяем, что владелец привязался автоматически
        self.assertEqual(response.data["owner"], self.user1.id)

    def test_create_habit_unauthorized(self):
        """Неавторизованный не может создать привычку"""
        data = {"place": "Дом", "time": "12:00:00", "action": "Тест"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_foreign_habit_forbidden(self):
        """User2 не может удалить привычку User1"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("habit-detail", kwargs={"pk": self.habit.pk})
        response = self.client.delete(url)
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )  # Или 403, в зависимости от queryset

    def test_validation_reward_and_related_habit(self):
        """Нельзя указать одновременно вознаграждение и связанную привычку"""
        self.client.force_authenticate(user=self.user1)
        # Создаем приятную привычку для связи
        pleasant_habit = Habit.objects.create(
            owner=self.user1,
            place="Дом",
            time="13:00:00",
            action="Съесть конфету",
            is_pleasant=True,
        )
        data = {
            "place": "Улица",
            "time": "14:00:00",
            "action": "Гулять",
            "reward": "Купить мороженое",
            "related_habit": pleasant_habit.id,
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("related_habit", response.data)

    def test_validation_time_to_action_max_120_sec(self):
        """Время выполнения не должно превышать 120 секунд"""
        self.client.force_authenticate(user=self.user1)
        data = {
            "place": "Зал",
            "time": "15:00:00",
            "action": "Бег",
            "time_to_action": "00:03:00",  # 3 минуты = 180 секунд
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("time_to_action", response.data)

    def test_public_habits_available_to_unauthorized(self):
        """Неавторизованный видит только публичные привычки"""
        # Создаем непубличную привычку от user2
        Habit.objects.create(
            owner=self.user2,
            place="Дом",
            time="20:00:00",
            action="Спать",
            is_published=False,
        )

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должен быть только 1 результат (публичная привычка user1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["action"], "Отжаться")

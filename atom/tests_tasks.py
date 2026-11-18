from django.test import TestCase
from unittest.mock import patch
from datetime import datetime, timedelta
from .models import Habit
from man.models import Gent
from .tasks import send_habit_reminders
import pytz


class TasksTestCase(TestCase):
    def setUp(self):
        self.user = Gent.objects.create_user(
            username="testuser", password="123", chat_id="123456789"
        )
        # Создаем привычку на текущее время
        now = datetime.now(pytz.timezone("Europe/Moscow"))
        self.habit = Habit.objects.create(
            owner=self.user,
            place="Дом",
            time=now.time().replace(second=0, microsecond=0),
            action="Отжаться",
            time_to_action=timedelta(seconds=60),
            period=1,
        )

    @patch("atom.tasks.requests.post")
    def test_send_habit_reminders_success(self, mock_post):
        """Проверяем, что задача отправляет сообщение, если время совпало"""
        # Настраиваем мок, чтобы он имитировал успешный ответ от Telegram
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status.return_value = None

        # Вызываем задачу
        send_habit_reminders()

        # Проверяем, что requests.post был вызван (сообщение "отправлено")
        self.assertTrue(mock_post.called)

    @patch("atom.tasks.requests.post")
    def test_send_habit_reminders_no_chat_id(self, mock_post):
        """Если у пользователя нет chat_id, задача не отправляет сообщение"""
        self.user.chat_id = ""
        self.user.save()

        send_habit_reminders()
        self.assertFalse(mock_post.called)  # Отправки не было

from celery import shared_task
from django.utils import timezone
from django.core.exceptions import ValidationError
import requests


from atom.models import Habit
from atom.validators import validate_last_completion
import asyncio
from telegram import Bot
from django.conf import settings


@shared_task
def send_habit_reminders():
    now = timezone.localtime(timezone.now())
    current_time = now.time().replace(second=0, microsecond=0)
    today = now.date()

    print(f"--- ЗАПУСК ЗАДАЧИ. Время сервера: {current_time} ---")  # <--- ДОБАВИТЬ

    # Ищем привычки, время которых подошло
    habits = Habit.objects.filter(
        time__hour=current_time.hour,
        time__minute=current_time.minute
    )

    print(f"Найдено привычек на это время: {habits.count()}")  # <--- ДОБАВИТЬ

    for habit in habits:
        print(f"Проверяем привычку: {habit.action}")  # <--- ДОБАВИТЬ
        last_completion = habit.completions.order_by("-completed_at").first()

        # 1. Не спамим, если привычка уже выполнена сегодня
        if last_completion and last_completion.completed_at.date() == today:
            print("Пропуск: привычка уже выполнена сегодня")  # <--- ДОБАВИТЬ
            continue

        # 2. Учитываем периодичность (period)
        # Если привычка раз в 3 дня, а последнее выполнение было вчера — пропускаем
        if habit.period > 1 and last_completion:
            days_since_last = (today - last_completion.completed_at.date()).days
            if days_since_last < habit.period:
                continue

        if not habit.owner.chat_id:
            print(f"Пропуск: периодичность. Прошло дней: {days_since_last}")  # <--- ДОБАВИТЬ
            continue

        # 3. Формируем текст сообщения
        text = f"⏰ Время выполнить привычку!\nДействие: {habit.action}\nМесто: {habit.place}"

        # 4. Проверяем на "заброшенность" и добавляем предупреждение
        try:
            validate_last_completion(habit)
        except ValidationError as e:
            text += f"\n\n⚠️ {e.message}"

        print(f"Отправка сообщения для {habit.owner.username} на chat_id {habit.owner.chat_id}")  # <--- ДОБАВИТЬ

        # 5. Отправка
        token = settings.TELEGRAM_TOKEN
        url = f"https://api.telegram.org/bot{token}/sendMessage"

        try:
            requests.post(url, json={"chat_id": habit.owner.chat_id, "text": text}, timeout=10)
        except requests.RequestException as e:
            print(f"Ошибка отправки в Telegram для привычки {habit.id}: {e}")

        if not habit.owner.chat_id:
            continue

        text = f"⏰ Напоминание: {habit.action} в {habit.place}"

        # Отправка через python-telegram-bot
        bot = Bot(token=settings.TELEGRAM_TOKEN)

        # В синхронном Celery используем asyncio.run для асинхронной отправки
        asyncio.run(bot.send_message(chat_id=habit.owner.chat_id, text=text))

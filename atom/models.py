from django.utils import timezone

from django.db import models

from man.models import Gent

NULLABLE = {"null": True, "blank": True}


class Habit(models.Model):
    owner = models.ForeignKey(
        Gent, on_delete=models.CASCADE, **NULLABLE, verbose_name="Создатель"
    )
    place = models.CharField(max_length=100, verbose_name="Место")
    time = models.TimeField(default=timezone.now(), verbose_name="Время выполнения")
    action = models.CharField(max_length=100, verbose_name="Действие")
    connection_wont = models.ForeignKey(
        "self", on_delete=models.SET_NULL, **NULLABLE, verbose_name="Связанная привычка"
    )
    period = models.PositiveIntegerField()
    reward = models.CharField(max_length=100, **NULLABLE, verbose_name="Вознаграждение")
    time_to_action = models.DurationField(
        default=timezone.timedelta(seconds=60), verbose_name="Время на выполнение"
    )
    is_published = models.BooleanField(default=True, verbose_name="Признак публичности")

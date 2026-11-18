from django.contrib.auth.models import AbstractUser
from django.db import models


class Gent(AbstractUser):
    chat_id = models.CharField(max_length=225, blank=True, null=True)

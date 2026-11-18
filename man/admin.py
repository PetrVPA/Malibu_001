from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from man.models import Gent


# Регистрируем кастомную модель пользователя
@admin.register(Gent)
class GentAdmin(UserAdmin):
    # Добавляем поле chat_id в отображение в админке
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("chat_id",)}),)
    list_display = ("username", "email", "chat_id", "is_staff")

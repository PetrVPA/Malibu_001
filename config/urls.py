

from rest_framework.routers import DefaultRouter
from atom.views import HabitViewSet
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from man.views import RegisterView

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')

# Настройка схемы Swagger
schema_view = get_schema_view(
   openapi.Info(
      title="API Трекера привычек",
      default_version='v1',
      description="Документация для курсового проекта по трекеру привычек",
      contact=openapi.Contact(email="admin@example.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,), # Разрешаем смотреть всем
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('atom.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='register'),

    # --- МАРШРУТЫ ДЛЯ ДОКУМЕНТАЦИИ (SWAGGER) ---
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
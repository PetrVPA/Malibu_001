

from rest_framework.routers import DefaultRouter
from atom.views import HabitViewSet
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('atom.urls')),
]
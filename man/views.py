from rest_framework import generics
from rest_framework.permissions import AllowAny
from man.models import Gent
from man.serializers import GentSerializer  # Вам нужно будет создать этот сериализатор


class RegisterView(generics.CreateAPIView):
    queryset = Gent.objects.all()
    permission_classes = (AllowAny,)  # Доступно без авторизации
    serializer_class = GentSerializer

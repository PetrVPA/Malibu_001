from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class UserRegistrationTest(APITestCase):
    def test_register_user(self):
        """Тест успешной регистрации нового пользователя"""
        url = reverse("register")  # Убедитесь, что name='register' указан в urls.py
        data = {
            "username": "testuser",
            "password": "testpassword123",
            "chat_id": "123456789",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_get_jwt_token(self):
        """Тест получения JWT токена (авторизация)"""
        User.objects.create_user(
            username="authuser", password="password123", chat_id="111"
        )
        url = reverse("token_obtain_pair")  # name='token_obtain_pair' из SimpleJWT
        data = {"username": "authuser", "password": "password123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import User
import uuid


class GetTelegramLinkAPIView(APIView):
    """
    API для генерации ссылки на бота для регистрации пользователя.
    """

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.telegram_token = str(uuid.uuid4())  # Генерируем новый токен
        user.save()

        bot_username = settings.TELEGRAM_BOT_USERNAME  # Имя бота из settings
        link = f"https://t.me/{bot_username}?start=register_{user.telegram_token}"
        return Response({"telegram_link": link}, status=status.HTTP_200_OK)


class RegisterTelegramAPIView(APIView):
    """
    API для привязки Telegram ID пользователя.
    """

    def post(self, request):
        telegram_id = request.data.get("telegram_id")
        token = request.data.get("token")

        if not telegram_id or not token:
            return Response({"error": "telegram_id и token обязательны"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(telegram_token=token).first()
        if not user:
            return Response({"error": "Неверный или устаревший токен"}, status=status.HTTP_400_BAD_REQUEST)

        user.telegram_id = telegram_id
        user.telegram_token = None  # Очищаем токен после успешной привязки
        user.save()
        data = {
            "user": {
                "id": user.id,
                "company_name": user.company.name,
            },
            "message": "✅ Telegram успешно привязан!"
        }

        return Response(data, status=status.HTTP_200_OK)

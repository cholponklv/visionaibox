from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import User

def get_telegram_link(request, user_id):
    """Генерирует ссылку на бота для регистрации"""
    user = get_object_or_404(User, id=user_id)
    user.generate_telegram_token()  # Генерируем токен
    bot_username = settings.TELEGRAM_BOT_USERNAME  # Указываем имя бота
    link = f"https://t.me/{bot_username}?start=register_{user.telegram_token}"
    return JsonResponse({"telegram_link": link})

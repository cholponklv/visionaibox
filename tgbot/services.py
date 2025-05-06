import logging

import requests
from django.conf import settings
from algorithms.serializers import AlertSerializer  

BOT_URL = settings.BOT_ALERT_URL  
logger = logging.getLogger(__name__)

def send_alert_to_bot(alert, request, for_security=True):
    """
    Отправляет информацию о новом alert в бота по HTTP POST-запросу,
    используя `AlertSerializer` для преобразования данных.
    """
    if not BOT_URL:
        print("BOT_URL не задан в settings.")
        logger.error("BOT_URL не задан в settings.")
        return
    if for_security:
        users = alert.device.company.users.filter(is_security=True)
    else:
        users = alert.device.company.users.filter(is_executive=True)
    users_telegram_id = [user.telegram_id for user in users if user.telegram_id]
    # Сериализуем Alert через `AlertSerializer`
    serialized_alert = AlertSerializer(alert, context={"request": request}).data
    serialized_alert["users_telegram_id"] = users_telegram_id
    serialized_alert["for_security"] = for_security

    # Отправляем POST-запрос
    try:
        response = requests.post(BOT_URL, json=serialized_alert, timeout=10)
        response_data = response.json()

        if response.status_code == 200 and response_data.get("error_code") == 0:
            print("Тревога успешно отправлена боту.")
        else:
            print(f"Ошибка отправки тревоги: {response_data}")
    except requests.RequestException as e:
        print(f"Ошибка сети при отправке тревоги: {e}")


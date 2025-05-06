from django.urls import path
from .views import GetTelegramLinkAPIView, RegisterTelegramAPIView

urlpatterns = [
    path("v1/get_telegram_link/<int:user_id>/", GetTelegramLinkAPIView.as_view(), name="get_telegram_link"),
    path("v1/register_telegram/", RegisterTelegramAPIView.as_view(), name="register_telegram"),
]

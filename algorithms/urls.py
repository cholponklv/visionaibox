from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertViewSet
from .views import alert_stats
# Создаем router и регистрируем ViewSet
router = DefaultRouter()
router.register(r'alerts', AlertViewSet, basename='alert')

urlpatterns = [
    path('v1/', include(router.urls)),  # Включаем все маршруты из router
    path("alert-stats/", alert_stats, name="alert-stats"),
]

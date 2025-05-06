from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.decorators import action

from tgbot.services import send_alert_to_bot
from visionaibox.mixins import ActionSerializerClassMixin
from .models import Alert
from .serializers import AlertSerializer, AlertCreateSerializer, AlertActionSerializer


class AlertViewSet(ActionSerializerClassMixin,
                   mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Alert.objects.all().prefetch_related("device", "source", "alg", "company")
    serializer_class = AlertSerializer

    action_serializer_class = {
        "create": AlertCreateSerializer,
    }

    def create(self, request, *args, **kwargs):
        """Создание тревоги с кастомным ответом в формате AIBox"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            alert = serializer.save()
            send_alert_to_bot(alert, request, for_security=True)
            return Response({"error_code": 0, "message": "alert push successful", "data": None}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error_code": -1, "message": "client error", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="send-action")
    def send_action(self, request, pk=None):
        """
        Подтверждение или отклонение тревоги
        """
        alert = self.get_object()
        serializer = AlertActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        action = serializer.validated_data["action"]

        if action == "confirm":
            alert.confirm_alert()

            # Отправка учредителям
            send_alert_to_bot(alert, request, for_security=False)

            return Response({"message": "Тревога подтверждена"}, status=status.HTTP_200_OK)

        elif action == "reject":
            alert.reject_alert()
            alert.save()

            return Response({"message": "Тревога отклонена"}, status=status.HTTP_200_OK)

        return Response({"error": "Неверное действие"}, status=status.HTTP_400_BAD_REQUEST)
import datetime
import base64
import uuid
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers

from companies.serializers import CompanySerializer
from devices.serializers import DeviceSerializer, SourceSerializer
from .models import Alert, Algorithm
from devices.models import Device, Source
from django.conf import settings


class AlgorithmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Algorithm
        fields = ("id", "key", "name", "type")


class AlertCreateSerializer(serializers.Serializer):
    id = serializers.CharField(write_only=True)  # AIBox `id` → `aibox_alert_id`
    alert_time = serializers.FloatField()
    device = serializers.DictField(write_only=True)
    source = serializers.DictField(write_only=True, required=False, allow_null=True)
    alg = serializers.DictField(write_only=True, required=False, allow_null=True)
    hazard_level = serializers.CharField(default="1", required=False, allow_null=True, allow_blank=True)

    image = serializers.CharField(write_only=True, required=False, allow_null=True)
    video = serializers.CharField(write_only=True, required=False, allow_null=True)

    reserved_data = serializers.JSONField(required=False, allow_null=True)
    company = serializers.StringRelatedField(read_only=True)

    def validate_id(self, value):
        """Проверяем, что `id` не пустой"""
        if not value:
            raise serializers.ValidationError("Поле 'id' обязательно.")
        if Alert.objects.filter(aibox_alert_id=value).exists():
            raise serializers.ValidationError("Тревога с таким 'id' уже существует.")
        return value

    def validate_alert_time(self, value):
        """Конвертируем timestamp в `datetime`"""
        try:
            return datetime.datetime.fromtimestamp(value)
        except Exception:
            raise serializers.ValidationError("Некорректный формат alert_time (должен быть timestamp).")

    def validate_device(self, value):
        """Проверяем, что устройство существует, иначе выбрасываем ошибку"""
        device_id = value.get("id")
        if not device_id:
            raise serializers.ValidationError("Поле 'device.id' обязательно.")
        try:
            return Device.objects.get(aibox_id=device_id)
        except Device.DoesNotExist:
            raise serializers.ValidationError("Указанное устройство (Device) не найдено в базе данных.")


    def validate_alg(self, value):
        """Создаем Algorithm, если его нет"""
        if not value:
            return None

        alg_key = value.get("name")
        if not alg_key:
            raise serializers.ValidationError("Поле 'alg.name' обязательно.")

        return value

    def validate_image(self, value):
        """Обрабатываем изображение в формате base64"""
        if value:
            try:
                image_data = base64.b64decode(value)
                return ContentFile(image_data, name=f"alert_{uuid.uuid4().hex}.jpg")
            except Exception as e:
                raise serializers.ValidationError(f"Ошибка обработки изображения: {str(e)}")
        return None

    def validate_video(self, value):
        """Обрабатываем видео в формате base64"""
        if value:
            try:
                video_data = base64.b64decode(value)
                return ContentFile(video_data, name=f"alert_{uuid.uuid4().hex}.mp4")
            except Exception as e:
                raise serializers.ValidationError(f"Ошибка обработки видео: {str(e)}")
        return None

    def create(self, validated_data):
        """Создаёт Alert, обрабатывая `device`, `source`, `alg`, а также base64-изображения и видео."""
        device = validated_data.pop("device")
        source_data = validated_data.pop("source")
        alg_data = validated_data.pop("alg")
        image = validated_data.pop("image")
        video = validated_data.pop("video", None)
        aibox_alert_id = validated_data.pop("id")

        with transaction.atomic():
            source = None
            if source_data:
                source_id = source_data.get("id")
                source, _ = Source.objects.get_or_create(
                    source_id=source_id, device=device,
                    defaults={"ipv4": source_data.get("ipv4", ""), "desc": source_data.get("desc", "")}
                )

            algorithm = None
            if alg_data:
                alg_key = alg_data.get("name")
                algorithm, _ = Algorithm.objects.get_or_create(
                    key=alg_key,
                    defaults={"name": alg_data.get("ch_name", ""), "type": alg_data.get("type", "")}
                )

            alert = Alert.objects.create(
                aibox_alert_id=aibox_alert_id,
                device=device,
                source=source,
                alg=algorithm,
                company=device.company,
                **validated_data
            )

            if image:
                alert.image.save(image.name, image, save=True)
            if video:
                alert.video.save(video.name, video, save=True)

        return alert


class AlertSerializer(serializers.ModelSerializer):
    device = DeviceSerializer(read_only=True)
    source = SourceSerializer(read_only=True)
    alg = AlgorithmSerializer(read_only=True)
    company = CompanySerializer(read_only=True)

    class Meta:
        model = Alert
        fields = (
            "id", "aibox_alert_id", "alert_time", "device", "source", "alg", "hazard_level", "image", "video",
            "reserved_data", "company"
        )

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                print(1234)
                # Возвращаем полный URL с учетом домена
                return request.build_absolute_uri(obj.image.url)
            # Если request отсутствует, используем MEDIA_URL
            return f"{settings.MEDIA_URL}{obj.image}"

class AlertActionSerializer(serializers.Serializer):
    """Сериализатор для обработки подтверждения или отклонения тревоги"""
    action = serializers.ChoiceField(choices=["confirm", "reject"], required=True)

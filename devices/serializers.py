from .models import Device, Source
from rest_framework import serializers

class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ("id", "aibox_id", "name", "desc")


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ("id", "source_id", "ipv4", "desc", "device")


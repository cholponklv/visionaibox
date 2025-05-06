from django.contrib import admin
from .models import Device, Source

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "aibox_id", "company")
    search_fields = ("name", "aibox_id")
    list_filter = ("company",)

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("source_id", "ipv4", "device")
    search_fields = ("source_id", "ipv4")
    list_filter = ("device",)


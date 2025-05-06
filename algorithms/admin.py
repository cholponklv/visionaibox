from django.contrib import admin
from .models import Alert,Algorithm
# Register your models here.
@admin.register(Algorithm)
class AlgorithmAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "type")
    search_fields = ("name", "key")


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("id", "aibox_alert_id", "alert_time", "device", "source", "hazard_level", "company")
    list_filter = ("hazard_level", "company", "device")
    search_fields = ("aibox_alert_id", "device__name", "source__source_id")

from django.db import models
from devices.models import Device,Source
from companies.models import Company
from users.models import User
from django.utils.timezone import now

# Create your models here.
class Algorithm(models.Model):
    key = models.CharField(max_length=255, unique=True, help_text="Уникальный ключ алгоритма")
    name = models.CharField(max_length=255, help_text="Название алгоритма")
    type = models.CharField(max_length=255, help_text="Тип алгоритма")

    def __str__(self):
        return f"{self.name} ({self.key})"


# Create your models here.
class Alert(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Ожидание"),
        (STATUS_CONFIRMED, "Подтверждено"),
        (STATUS_REJECTED, "Отклонено"),
    ]
    aibox_alert_id = models.CharField(max_length=255, unique=True)
    alert_time = models.DateTimeField()
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="alerts", help_text="AIBox-устройство")
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="alerts", help_text="Источник (камера)")
    alg = models.ForeignKey(Algorithm, on_delete=models.SET_NULL, null=True, blank=True, related_name="alerts", help_text="Алгоритм, сработавший на тревогу")
    hazard_level = models.CharField(help_text="Уровень опасности", default='1')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="alerts", help_text="Компания, связанная с тревогой")
    image = models.ImageField(upload_to="alerts/images/", null=True, blank=True, help_text="Изображение тревоги (если есть)")
    video = models.FileField(upload_to="alerts/videos/", null=True, blank=True, help_text="Видео тревоги (если есть)")
    reserved_data = models.JSONField(help_text="Дополнительные данные от AIBox", null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending", help_text="Статус тревоги")
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="confirmed_alerts")
    confirmed_at = models.DateTimeField(null=True, blank=True, help_text="Время подтверждения тревоги")
    rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="rejected_alerts")
    rejected_at = models.DateTimeField(null=True, blank=True, help_text="Время отклонения тревоги")
    executive_users = models.ManyToManyField(User, related_name="executive_alerts", blank=True, help_text="Учредители")
    

    def __str__(self):
        return f"Alert {self.airbus_alert_id}"
    
    @property
    def is_pending(self):
        return self.status == self.STATUS_PENDING

    @property
    def is_confirmed(self):
        return self.status == self.STATUS_CONFIRMED

    @property
    def is_rejected(self):
        return self.status == self.STATUS_REJECTED

    def confirm_alert(self, user=None):
        """Подтверждает тревогу и записывает время и пользователя, который подтвердил."""
        self.status = self.STATUS_CONFIRMED
        self.confirmed_by = user
        print(user)
        self.confirmed_at = now() 
        self.save()

    def reject_alert(self, user=None):
        """Отклоняет тревогу и записывает пользователя, который отклонил."""
        self.status = self.STATUS_REJECTED
        self.rejected_by = user
        print(user)
        self.rejected_at = now()
        self.save()

    def save(self, *args, **kwargs):
        """Если `device` задан, автоматически устанавливаем `company`"""
        if self.device and not self.company_id:
            self.company = self.device.company
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Тревога {self.aibox_alert_id}"

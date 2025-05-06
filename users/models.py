import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from companies.models import Company

class UserManager(BaseUserManager):
    def create_user(self, telegram_id=None, email=None, password=None, **extra_fields):
        if not telegram_id and not email:
            raise ValueError("Пользователь должен иметь либо Telegram ID, либо email")

        extra_fields.setdefault("is_active", True)

        user = self.model(telegram_id=telegram_id, email=self.normalize_email(email) if email else None, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("company", None)  # У суперпользователя нет компании

        return self.create_user(email=email, password=password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True, help_text="Telegram ID пользователя")
    email = models.EmailField(unique=True, null=True, blank=True, help_text="Email пользователя")
    full_name = models.CharField(max_length=255, blank=True, null=True, help_text="Полное имя")
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, help_text="Компания пользователя",
                                related_name="users")
    is_active = models.BooleanField(default=True, help_text="Активен ли пользователь")
    is_staff = models.BooleanField(default=False, help_text="Является ли пользователь администратором")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Дата регистрации")
    telegram_token = models.CharField(max_length=255, unique=True, null=True, blank=True)  # Уникальный токен

    is_security = models.BooleanField(default=False, help_text="Сотрудник службы безопасности")
    is_executive = models.BooleanField(default=False, help_text="Учредитель компании")

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.full_name or self.email or f"Telegram User {self.telegram_id}"

    def save(self, *args, **kwargs):
        """Автоматически определяет роли пользователя"""
        if self.is_security and self.is_executive:
            raise ValueError("Пользователь не может быть одновременно сотрудником СБ и учредителем.")
        super().save(*args, **kwargs)

    @property
    def is_bot_user(self):
        """ Проверяем, является ли пользователь бот-пользователем """
        return bool(self.telegram_id and not self.email)

    def generate_telegram_token(self):
        """Генерирует уникальный токен для привязки Telegram"""
        self.telegram_token = str(uuid.uuid4())  # Генерируем уникальный токен
        self.save()

    def clear_telegram_token(self):
        """Очищает токен после успешной привязки"""
        self.telegram_token = None
        self.save()

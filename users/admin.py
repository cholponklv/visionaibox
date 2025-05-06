from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "full_name", "telegram_id", "company", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active", "company")
    search_fields = ("email", "full_name", "telegram_id")
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Персональная информация", {"fields": ("full_name", "company")}),
        ("Права", {"fields": ("is_active", "is_staff", "is_superuser", "is_security", "is_executive", "groups",
                              "user_permissions")}),
        ("Даты", {"fields": ("last_login", )}),
        ("Telegram", {"fields": ("telegram_id", "telegram_token",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_active"),
        }),
    )

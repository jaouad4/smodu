"""Admin du module notifications."""

from django.contrib import admin
from .models import Notification, NotificationPreferences


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["recipient", "notification_type", "title", "is_read", "created_at"]
    list_filter = ["notification_type", "is_read"]
    search_fields = ["recipient__email", "title"]
    readonly_fields = ["created_at", "read_at"]


@admin.register(NotificationPreferences)
class NotificationPreferencesAdmin(admin.ModelAdmin):
    list_display = ["user", "inapp_all", "email_onboarding", "email_reminders"]
    search_fields = ["user__email"]

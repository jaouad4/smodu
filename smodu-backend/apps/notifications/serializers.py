"""Serializers du module notifications."""

from rest_framework import serializers
from .models import Notification, NotificationPreferences


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "title",
            "message",
            "action_url",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = fields


class NotificationPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreferences
        fields = [
            "email_onboarding",
            "email_courses",
            "email_quizzes",
            "email_competences",
            "email_reminders",
            "inapp_all",
            "updated_at",
        ]
        read_only_fields = ["updated_at"]

"""Modèles du module notifications : in-app et email."""

import uuid
from django.db import models
from apps.users.models import CustomUser


class NotificationType(models.TextChoices):
    ONBOARDING_ASSIGNED = "ONBOARDING_ASSIGNED", "Parcours d'onboarding assigné"
    ONBOARDING_COMPLETED = "ONBOARDING_COMPLETED", "Onboarding complété"
    COURSE_ENROLLED = "COURSE_ENROLLED", "Inscription à un cours"
    COURSE_COMPLETED = "COURSE_COMPLETED", "Cours terminé"
    QUIZ_PASSED = "QUIZ_PASSED", "Quiz réussi"
    QUIZ_FAILED = "QUIZ_FAILED", "Quiz échoué"
    COMPETENCE_VALIDATED = "COMPETENCE_VALIDATED", "Compétence validée"
    DUE_DATE_REMINDER = "DUE_DATE_REMINDER", "Rappel de date limite"
    VALIDATION_REQUESTED = "VALIDATION_REQUESTED", "Validation de projet demandée"
    VALIDATION_APPROVED = "VALIDATION_APPROVED", "Validation de projet approuvée"
    VALIDATION_REJECTED = "VALIDATION_REJECTED", "Validation de projet refusée"
    SYSTEM = "SYSTEM", "Message système"


class Notification(models.Model):
    """Notification in-app pour un utilisateur."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Destinataire",
    )
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        verbose_name="Type",
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")
    action_url = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="URL d'action (frontend)",
        help_text="Ex: /formation/courses/uuid",
    )
    is_read = models.BooleanField(default=False, verbose_name="Lue")
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["recipient", "created_at"]),
        ]

    def __str__(self):
        status = "✓" if self.is_read else "●"
        return f"{status} [{self.recipient.email}] {self.title}"

    def mark_as_read(self):
        """Marque la notification comme lue."""
        from django.utils import timezone

        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])


class NotificationPreferences(models.Model):
    """Préférences de notification d'un utilisateur."""

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )
    email_onboarding = models.BooleanField(
        default=True, verbose_name="Email — Onboarding"
    )
    email_courses = models.BooleanField(default=True, verbose_name="Email — Cours")
    email_quizzes = models.BooleanField(default=True, verbose_name="Email — Quiz")
    email_competences = models.BooleanField(
        default=True, verbose_name="Email — Compétences"
    )
    email_reminders = models.BooleanField(default=True, verbose_name="Email — Rappels")
    inapp_all = models.BooleanField(
        default=True, verbose_name="Notifications in-app activées"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Préférences de notification"
        verbose_name_plural = "Préférences de notifications"

    def __str__(self):
        return f"Préférences de {self.user.email}"

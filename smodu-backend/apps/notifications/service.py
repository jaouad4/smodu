"""
Service centralisé pour créer des notifications.
Utilisé par tous les autres modules via import.
"""

from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, NotificationPreferences, NotificationType


def notify(
    recipient,
    notification_type: str,
    title: str,
    message: str,
    action_url: str = "",
    send_email: bool = False,
):
    """
    Crée une notification in-app et envoie optionnellement un email.

    Usage:
        from apps.notifications.service import notify, NotificationType

        notify(
            recipient=user,
            notification_type=NotificationType.QUIZ_PASSED,
            title="Quiz réussi !",
            message="Vous avez obtenu 85% au quiz Odoo Ventes.",
            action_url="/evaluations/my-attempts",
            send_email=True,
        )
    """
    # Vérifier les préférences in-app
    prefs, _ = NotificationPreferences.objects.get_or_create(user=recipient)
    if not prefs.inapp_all:
        return None

    notification = Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        action_url=action_url,
    )

    # Envoi email si demandé et si les préférences l'autorisent
    if send_email and _should_send_email(prefs, notification_type):
        _send_notification_email(recipient, title, message)

    return notification


def notify_bulk(
    recipients, notification_type: str, title: str, message: str, action_url: str = ""
):
    """Envoie la même notification à plusieurs utilisateurs."""
    notifications = []
    for recipient in recipients:
        prefs, _ = NotificationPreferences.objects.get_or_create(user=recipient)
        if prefs.inapp_all:
            notifications.append(
                Notification(
                    recipient=recipient,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    action_url=action_url,
                )
            )
    if notifications:
        Notification.objects.bulk_create(notifications)


def _should_send_email(prefs: NotificationPreferences, notification_type: str) -> bool:
    """Détermine si l'email doit être envoyé selon les préférences."""
    mapping = {
        NotificationType.ONBOARDING_ASSIGNED: prefs.email_onboarding,
        NotificationType.ONBOARDING_COMPLETED: prefs.email_onboarding,
        NotificationType.COURSE_ENROLLED: prefs.email_courses,
        NotificationType.COURSE_COMPLETED: prefs.email_courses,
        NotificationType.QUIZ_PASSED: prefs.email_quizzes,
        NotificationType.QUIZ_FAILED: prefs.email_quizzes,
        NotificationType.COMPETENCE_VALIDATED: prefs.email_competences,
        NotificationType.DUE_DATE_REMINDER: prefs.email_reminders,
        NotificationType.VALIDATION_REQUESTED: prefs.email_onboarding,
        NotificationType.VALIDATION_APPROVED: prefs.email_onboarding,
        NotificationType.VALIDATION_REJECTED: prefs.email_onboarding,
    }
    return mapping.get(notification_type, True)


def _send_notification_email(recipient, subject: str, body: str):
    """Envoie un email de notification."""
    try:
        send_mail(
            subject=f"[SMODU] {subject}",
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            fail_silently=True,
        )
    except Exception:
        pass

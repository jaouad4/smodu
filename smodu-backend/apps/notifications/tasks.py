"""Tâches Celery pour les notifications différées et rappels."""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task(name="notifications.send_due_date_reminders")
def send_due_date_reminders():
    """
    Tâche planifiée quotidiennement.
    Envoie des rappels pour les assignments/inscriptions
    dont la date limite approche à J-3 et J-1.
    """
    from apps.onboarding.models import OnboardingAssignment
    from apps.formation.models import CourseEnrollment
    from .service import notify, NotificationType

    today = timezone.now().date()
    reminder_days = [1, 3]

    for days in reminder_days:
        target_date = today + timedelta(days=days)

        # Rappels onboarding
        for assignment in OnboardingAssignment.objects.filter(
            due_date=target_date
        ).select_related("user", "template"):
            if not assignment.is_completed:
                notify(
                    recipient=assignment.user,
                    notification_type=NotificationType.DUE_DATE_REMINDER,
                    title=f"Rappel : parcours à terminer dans {days} jour(s)",
                    message=(
                        f"Votre parcours d'onboarding « {assignment.template.title} » "
                        f"doit être terminé le {assignment.due_date.strftime('%d/%m/%Y')}."
                    ),
                    action_url="/onboarding/my-journey",
                    send_email=True,
                )

        # Rappels formation
        for enrollment in CourseEnrollment.objects.filter(
            due_date=target_date,
            completed_at__isnull=True,
        ).select_related("user", "course"):
            notify(
                recipient=enrollment.user,
                notification_type=NotificationType.DUE_DATE_REMINDER,
                title=f"Rappel : cours à terminer dans {days} jour(s)",
                message=(
                    f"Votre cours « {enrollment.course.title} » "
                    f"doit être terminé le {enrollment.due_date.strftime('%d/%m/%Y')}."
                ),
                action_url=f"/formation/courses/{enrollment.course.id}",
                send_email=True,
            )


@shared_task(name="notifications.cleanup_old_notifications")
def cleanup_old_notifications():
    """Supprime les notifications lues de plus de 90 jours."""
    from .models import Notification

    cutoff = timezone.now() - timedelta(days=90)
    deleted_count, _ = Notification.objects.filter(
        is_read=True,
        read_at__lt=cutoff,
    ).delete()
    return f"{deleted_count} notifications supprimées."

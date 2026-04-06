"""
Services d'agrégation pour le dashboard.
Calcule les KPIs en temps réel depuis les autres modules.
"""

from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from apps.users.models import CustomUser, Role
from apps.onboarding.models import OnboardingAssignment, StepCompletion
from apps.formation.models import CourseEnrollment, LessonProgress
from apps.evaluations.models import QuizAttempt
from apps.competences.models import CompetenceAcquisition


def get_learner_dashboard(user: CustomUser) -> dict:
    """
    Vue synthétique pour l'apprenant connecté.
    Retourne : onboarding, cours en cours, quiz récents, compétences.
    """
    # ── Onboarding ───────────────────────────────────────────────
    onboarding_assignments = OnboardingAssignment.objects.filter(user=user)
    onboarding_summary = []
    for assignment in onboarding_assignments.select_related("template"):
        onboarding_summary.append(
            {
                "id": str(assignment.id),
                "template_title": assignment.template.title,
                "progress_percentage": assignment.progress_percentage,
                "is_completed": assignment.is_completed,
                "due_date": assignment.due_date,
            }
        )

    # ── Formation ────────────────────────────────────────────────
    enrollments = CourseEnrollment.objects.filter(user=user).select_related("course")
    courses_summary = []
    for enrollment in enrollments:
        courses_summary.append(
            {
                "id": str(enrollment.id),
                "course_title": enrollment.course.title,
                "difficulty": enrollment.course.difficulty,
                "progress_percentage": enrollment.progress_percentage,
                "completed_at": enrollment.completed_at,
                "due_date": enrollment.due_date,
            }
        )

    # ── Quiz ─────────────────────────────────────────────────────
    recent_attempts = (
        QuizAttempt.objects.filter(user=user, submitted_at__isnull=False)
        .select_related("quiz")
        .order_by("-submitted_at")[:5]
    )
    quiz_summary = [
        {
            "quiz_title": a.quiz.title,
            "score": float(a.score) if a.score is not None else None,
            "is_passed": a.is_passed,
            "attempt_number": a.attempt_number,
            "submitted_at": a.submitted_at,
        }
        for a in recent_attempts
    ]

    # ── Compétences ───────────────────────────────────────────────
    acquisitions = CompetenceAcquisition.objects.filter(user=user).select_related(
        "competence__category"
    )
    total_competences = acquisitions.count()
    validated_competences = sum(1 for a in acquisitions if a.is_validated)

    return {
        "onboarding": onboarding_summary,
        "courses": courses_summary,
        "recent_quiz_attempts": quiz_summary,
        "competences": {
            "total": total_competences,
            "validated": validated_competences,
            "validation_rate": (
                round(validated_competences / total_competences * 100, 1)
                if total_competences
                else 0
            ),
        },
    }


def get_manager_dashboard() -> dict:
    """
    Vue globale pour le manager/admin.
    Retourne des KPIs agrégés sur tous les apprenants.
    """
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    # ── Utilisateurs ──────────────────────────────────────────────
    learners = CustomUser.objects.filter(role=Role.LEARNER, is_active=True)
    total_learners = learners.count()
    new_learners_30d = learners.filter(date_joined__gte=thirty_days_ago).count()

    # ── Onboarding ───────────────────────────────────────────────
    all_assignments = OnboardingAssignment.objects.all()
    total_assignments = all_assignments.count()
    completed_assignments = sum(1 for a in all_assignments if a.is_completed)
    overdue_assignments = (
        all_assignments.filter(
            due_date__lt=now.date(),
        )
        .exclude(id__in=[a.id for a in all_assignments if a.is_completed])
        .count()
    )

    # ── Formation ─────────────────────────────────────────────────
    all_enrollments = CourseEnrollment.objects.all()
    total_enrollments = all_enrollments.count()
    completed_enrollments = all_enrollments.filter(completed_at__isnull=False).count()

    # ── Quiz ─────────────────────────────────────────────────────
    submitted_attempts = QuizAttempt.objects.filter(submitted_at__isnull=False)
    total_attempts = submitted_attempts.count()
    passed_attempts = submitted_attempts.filter(is_passed=True).count()
    avg_score = submitted_attempts.aggregate(avg=Avg("score"))["avg"]

    # ── Activité récente (30 jours) ───────────────────────────────
    recent_completions = StepCompletion.objects.filter(
        completed_at__gte=thirty_days_ago
    ).count()
    recent_lesson_progress = LessonProgress.objects.filter(
        last_accessed__gte=thirty_days_ago,
        is_completed=True,
    ).count()

    # ── Top apprenants (par compétences validées) ─────────────────
    top_learners = (
        CompetenceAcquisition.objects.filter(
            user__role=Role.LEARNER, user__is_active=True
        )
        .values("user__id", "user__first_name", "user__last_name", "user__email")
        .annotate(validated_count=Count("id", filter=Q(level__gte=1)))
        .order_by("-validated_count")[:5]
    )

    return {
        "kpis": {
            "total_learners": total_learners,
            "new_learners_30d": new_learners_30d,
            "total_onboarding_assignments": total_assignments,
            "completed_onboarding": completed_assignments,
            "onboarding_completion_rate": (
                round(completed_assignments / total_assignments * 100, 1)
                if total_assignments
                else 0
            ),
            "overdue_onboarding": overdue_assignments,
            "total_enrollments": total_enrollments,
            "completed_enrollments": completed_enrollments,
            "course_completion_rate": (
                round(completed_enrollments / total_enrollments * 100, 1)
                if total_enrollments
                else 0
            ),
            "total_quiz_attempts": total_attempts,
            "quiz_pass_rate": (
                round(passed_attempts / total_attempts * 100, 1)
                if total_attempts
                else 0
            ),
            "avg_quiz_score": round(float(avg_score), 1) if avg_score else 0,
        },
        "activity_30d": {
            "onboarding_steps_completed": recent_completions,
            "lessons_completed": recent_lesson_progress,
        },
        "top_learners": list(top_learners),
    }


def get_learner_progress_report(user_id: str) -> dict:
    """
    Rapport détaillé d'un apprenant pour le manager.
    """
    user = CustomUser.objects.get(id=user_id)
    learner_data = get_learner_dashboard(user)

    # Compétences détaillées
    acquisitions = CompetenceAcquisition.objects.filter(user=user).select_related(
        "competence__category"
    )
    competences_by_category = {}
    for acq in acquisitions:
        cat = acq.competence.category.name
        if cat not in competences_by_category:
            competences_by_category[cat] = {"total": 0, "validated": 0, "items": []}
        competences_by_category[cat]["total"] += 1
        if acq.is_validated:
            competences_by_category[cat]["validated"] += 1
        competences_by_category[cat]["items"].append(
            {
                "name": acq.competence.name,
                "level": acq.level,
                "required": acq.competence.level_required,
                "is_validated": acq.is_validated,
            }
        )

    return {
        "user": {
            "id": str(user.id),
            "full_name": user.get_full_name(),
            "email": user.email,
            "role": user.role,
            "department": user.department,
            "date_joined": user.date_joined,
        },
        **learner_data,
        "competences_by_category": competences_by_category,
    }

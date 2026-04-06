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
    Retourne des KPIs agrégés sur tous les apprenants + liste détaillée.
    """
    learners_qs = CustomUser.objects.filter(
        role=Role.LEARNER, is_active=True
    ).select_related("profile")

    learners_list = []
    completion_rates = []

    for u in learners_qs:
        # Compétences
        acquisitions = CompetenceAcquisition.objects.filter(user=u)
        total = acquisitions.count()
        validated = sum(1 for a in acquisitions if a.is_validated)

        completion_pct = round(validated / total * 100) if total else 0
        completion_rates.append(completion_pct)

        # Quiz
        attempts = QuizAttempt.objects.filter(user=u, submitted_at__isnull=False)
        avg_score_raw = attempts.aggregate(avg=Avg("score"))["avg"]
        quiz_avg = round(float(avg_score_raw), 1) if avg_score_raw else 0

        profile = getattr(u, "profile", None)
        project_status = profile.project_status if profile else "ONBOARDING"

        learners_list.append(
            {
                "user": {
                    "id": str(u.id),
                    "full_name": u.get_full_name(),
                    "email": u.email,
                    "department": u.department,
                },
                "completion_percentage": completion_pct,
                "quiz_avg_score": quiz_avg,
                "project_status": project_status,
            }
        )

    total_learners = len(learners_list)
    validated_count = sum(
        1 for l in learners_list if l["project_status"] == "VALIDATED"
    )
    delayed_count = sum(1 for l in learners_list if l["project_status"] == "NOT_READY")
    avg_completion = (
        round(sum(completion_rates) / len(completion_rates), 1)
        if completion_rates
        else 0
    )

    return {
        "kpis": {
            "active_learners": total_learners,
            "avg_completion_rate": avg_completion,
            "validated_learners": validated_count,
            "delayed_learners": delayed_count,
        },
        "learners": learners_list,
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

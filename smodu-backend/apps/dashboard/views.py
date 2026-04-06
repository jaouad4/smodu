"""Vues du module dashboard."""

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

from apps.users.permissions import IsManagerOrAdmin
from apps.users.models import CustomUser
from .services import (
    get_learner_dashboard,
    get_manager_dashboard,
    get_learner_progress_report,
)


class LearnerDashboardView(APIView):
    """GET /api/dashboard/me/ — tableau de bord de l'apprenant connecté."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = get_learner_dashboard(request.user)
        return Response(data)


class ManagerDashboardView(APIView):
    """GET /api/dashboard/manager/ — KPIs globaux pour le manager/admin."""

    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        data = get_manager_dashboard()
        return Response(data)


class LearnerReportView(APIView):
    """GET /api/dashboard/learners/{id}/report/ — rapport individuel d'un apprenant."""

    permission_classes = [IsManagerOrAdmin]

    def get(self, request, pk):
        try:
            data = get_learner_progress_report(str(pk))
            return Response(data)
        except CustomUser.DoesNotExist:
            return Response(
                {"detail": "Utilisateur introuvable."},
                status=status.HTTP_404_NOT_FOUND,
            )


class LearnersListView(APIView):
    """GET /api/dashboard/learners/ — liste des apprenants avec leur progression."""

    permission_classes = [IsManagerOrAdmin]

    def get(self, request):
        from apps.users.models import Role
        from apps.onboarding.models import OnboardingAssignment
        from apps.formation.models import CourseEnrollment

        learners = (
            CustomUser.objects.filter(role=Role.LEARNER, is_active=True)
            .select_related("profile")
            .order_by("-date_joined")
        )

        result = []
        for user in learners:
            # Progression onboarding
            assignments = OnboardingAssignment.objects.filter(user=user)
            total_ob = assignments.count()
            completed_ob = sum(1 for a in assignments if a.is_completed)

            # Progression formation
            enrollments = CourseEnrollment.objects.filter(user=user)
            total_en = enrollments.count()
            completed_en = enrollments.filter(completed_at__isnull=False).count()

            result.append(
                {
                    "id": str(user.id),
                    "full_name": user.get_full_name(),
                    "email": user.email,
                    "department": user.department,
                    "date_joined": user.date_joined,
                    "project_status": (
                        getattr(user.profile, "project_status", "N/A")
                        if hasattr(user, "profile")
                        else "N/A"
                    ),
                    "onboarding": {
                        "total": total_ob,
                        "completed": completed_ob,
                        "rate": (
                            round(completed_ob / total_ob * 100, 1) if total_ob else 0
                        ),
                    },
                    "formation": {
                        "total": total_en,
                        "completed": completed_en,
                        "rate": (
                            round(completed_en / total_en * 100, 1) if total_en else 0
                        ),
                    },
                }
            )

        return Response(result)

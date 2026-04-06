"""Vues du module formation."""

from django.db import transaction
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsManagerOrAdmin, IsTrainerOrAdmin
from .models import Course, CourseEnrollment, LessonProgress, Lesson
from .serializers import (
    CourseListSerializer,
    CourseDetailSerializer,
    CourseEnrollmentSerializer,
    EnrollmentCreateSerializer,
    LessonProgressSerializer,
    LessonProgressUpdateSerializer,
)


class CourseListView(generics.ListAPIView):
    """GET /api/formation/courses/ — liste des cours publiés."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CourseListSerializer

    def get_queryset(self):
        qs = Course.objects.filter(is_published=True)
        difficulty = self.request.query_params.get("difficulty")
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        return qs


class CourseAdminListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/formation/admin/courses/ — gestion complète (formateur/admin)."""

    permission_classes = [IsTrainerOrAdmin]

    def get_queryset(self):
        return Course.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CourseDetailSerializer
        return CourseListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/formation/courses/{id}/ — détail d'un cours."""

    permission_classes = [permissions.IsAuthenticated]
    queryset = Course.objects.prefetch_related("modules__lessons")
    serializer_class = CourseDetailSerializer


class MyCoursesView(generics.ListAPIView):
    """GET /api/formation/my-courses/ — cours de l'apprenant connecté."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CourseEnrollmentSerializer

    def get_queryset(self):
        return (
            CourseEnrollment.objects.filter(user=self.request.user)
            .select_related("course")
            .prefetch_related("lesson_progresses")
        )


class EnrollmentListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/formation/enrollments/ — inscriptions (manager/admin)."""

    permission_classes = [IsManagerOrAdmin]

    def get_queryset(self):
        return CourseEnrollment.objects.select_related("user", "course", "enrolled_by")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return EnrollmentCreateSerializer
        return CourseEnrollmentSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(enrolled_by=self.request.user)


class LessonProgressView(APIView):
    """
    GET  /api/formation/lessons/{id}/progress/ — progression sur une leçon
    POST /api/formation/lessons/{id}/progress/ — mettre à jour la progression
    """

    permission_classes = [permissions.IsAuthenticated]

    def _get_enrollment(self, user, lesson):
        return CourseEnrollment.objects.filter(
            user=user,
            course=lesson.module.course,
        ).first()

    def get(self, request, pk):
        lesson = generics.get_object_or_404(Lesson, pk=pk)
        enrollment = self._get_enrollment(request.user, lesson)
        if not enrollment:
            return Response(
                {"detail": "Non inscrit à ce cours."}, status=status.HTTP_403_FORBIDDEN
            )

        progress, _ = LessonProgress.objects.get_or_create(
            enrollment=enrollment, lesson=lesson
        )
        return Response(LessonProgressSerializer(progress).data)

    @transaction.atomic
    def post(self, request, pk):
        lesson = generics.get_object_or_404(Lesson, pk=pk)
        enrollment = self._get_enrollment(request.user, lesson)
        if not enrollment:
            return Response(
                {"detail": "Non inscrit à ce cours."}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = LessonProgressUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        progress, _ = LessonProgress.objects.get_or_create(
            enrollment=enrollment, lesson=lesson
        )

        if "is_completed" in data:
            progress.is_completed = data["is_completed"]
            if data["is_completed"] and not progress.completed_at:
                progress.completed_at = timezone.now()

        if "time_spent_minutes" in data:
            progress.time_spent_minutes += data["time_spent_minutes"]

        progress.save()

        # Mettre à jour completed_at sur l'enrollment si 100%
        if enrollment.progress_percentage == 100 and not enrollment.completed_at:
            enrollment.completed_at = timezone.now()
            enrollment.save(update_fields=["completed_at"])

        return Response(
            {
                "detail": "Progression mise à jour.",
                "progress_percentage": enrollment.progress_percentage,
            }
        )

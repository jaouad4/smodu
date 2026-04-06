"""Serializers du module formation."""

from rest_framework import serializers
from .models import Course, CourseModule, Lesson, CourseEnrollment, LessonProgress


class LessonSerializer(serializers.ModelSerializer):
    """Leçon individuelle."""

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "content_type",
            "content",
            "content_url",
            "duration_minutes",
            "order",
            "is_free_preview",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CourseModuleSerializer(serializers.ModelSerializer):
    """Module avec ses leçons."""

    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.IntegerField(source="lessons.count", read_only=True)

    class Meta:
        model = CourseModule
        fields = [
            "id",
            "title",
            "description",
            "order",
            "lessons_count",
            "lessons",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CourseListSerializer(serializers.ModelSerializer):
    """Cours — version allégée pour la liste."""

    modules_count = serializers.IntegerField(read_only=True)
    enrollments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "difficulty",
            "thumbnail",
            "duration_hours",
            "is_published",
            "modules_count",
            "enrollments_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CourseDetailSerializer(serializers.ModelSerializer):
    """Cours — version complète avec modules et leçons."""

    modules = CourseModuleSerializer(many=True, read_only=True)
    modules_count = serializers.IntegerField(read_only=True)
    enrollments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "difficulty",
            "thumbnail",
            "duration_hours",
            "is_published",
            "modules",
            "modules_count",
            "enrollments_count",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]


class LessonProgressSerializer(serializers.ModelSerializer):
    """Progression sur une leçon."""

    lesson_title = serializers.CharField(source="lesson.title", read_only=True)

    class Meta:
        model = LessonProgress
        fields = [
            "id",
            "lesson",
            "lesson_title",
            "is_completed",
            "time_spent_minutes",
            "last_accessed",
            "completed_at",
        ]
        read_only_fields = ["id", "last_accessed"]


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    """Inscription avec progression."""

    course = CourseListSerializer(read_only=True)
    progress_percentage = serializers.IntegerField(read_only=True)
    user_full_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = [
            "id",
            "user",
            "user_full_name",
            "course",
            "enrolled_by",
            "enrolled_at",
            "due_date",
            "completed_at",
            "progress_percentage",
        ]
        read_only_fields = ["id", "enrolled_at", "enrolled_by"]


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    """Créer une inscription."""

    class Meta:
        model = CourseEnrollment
        fields = ["user", "course", "due_date"]


class LessonProgressUpdateSerializer(serializers.Serializer):
    """Mettre à jour la progression sur une leçon."""

    is_completed = serializers.BooleanField(required=False)
    time_spent_minutes = serializers.IntegerField(required=False, min_value=0)

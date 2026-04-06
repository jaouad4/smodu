"""Admin du module formation."""

from django.contrib import admin
from .models import Course, CourseModule, Lesson, CourseEnrollment, LessonProgress


class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1
    fields = ["title", "order"]
    show_change_link = True


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ["title", "content_type", "order", "duration_minutes", "is_free_preview"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [CourseModuleInline]
    list_display = [
        "title",
        "difficulty",
        "is_published",
        "duration_hours",
        "created_by",
        "created_at",
    ]
    list_filter = ["difficulty", "is_published"]
    search_fields = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ["title", "course", "order"]
    list_filter = ["course"]


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ["user", "course", "enrolled_at", "due_date", "completed_at"]
    list_filter = ["course"]
    search_fields = ["user__email", "user__first_name"]


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = [
        "enrollment",
        "lesson",
        "is_completed",
        "time_spent_minutes",
        "last_accessed",
    ]
    list_filter = ["is_completed"]

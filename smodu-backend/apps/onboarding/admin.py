"""Admin du module onboarding."""

from django.contrib import admin
from .models import (
    OnboardingTemplate,
    OnboardingStep,
    OnboardingDocument,
    OnboardingAssignment,
    StepCompletion,
)


class OnboardingStepInline(admin.TabularInline):
    model = OnboardingStep
    extra = 1
    fields = ["title", "step_type", "order", "is_mandatory", "duration_minutes"]


class OnboardingDocumentInline(admin.TabularInline):
    model = OnboardingDocument
    extra = 0


@admin.register(OnboardingTemplate)
class OnboardingTemplateAdmin(admin.ModelAdmin):
    inlines = [OnboardingStepInline]
    list_display = ["title", "is_active", "created_by", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["title"]


@admin.register(OnboardingStep)
class OnboardingStepAdmin(admin.ModelAdmin):
    inlines = [OnboardingDocumentInline]
    list_display = ["title", "template", "step_type", "order", "is_mandatory"]
    list_filter = ["step_type", "is_mandatory"]


@admin.register(OnboardingAssignment)
class OnboardingAssignmentAdmin(admin.ModelAdmin):
    list_display = ["user", "template", "assigned_by", "due_date", "assigned_at"]
    list_filter = ["template"]
    search_fields = ["user__email", "user__first_name"]


@admin.register(StepCompletion)
class StepCompletionAdmin(admin.ModelAdmin):
    list_display = ["assignment", "step", "completed_at"]
    search_fields = ["assignment__user__email"]

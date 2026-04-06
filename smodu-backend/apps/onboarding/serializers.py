"""Serializers du module onboarding."""

from rest_framework import serializers
from .models import (
    OnboardingTemplate,
    OnboardingStep,
    OnboardingDocument,
    OnboardingAssignment,
    StepCompletion,
)


class OnboardingDocumentSerializer(serializers.ModelSerializer):
    """Serializer d'un document attaché à une étape."""

    class Meta:
        model = OnboardingDocument
        fields = ["id", "title", "file", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]


class OnboardingStepSerializer(serializers.ModelSerializer):
    """Serializer d'une étape avec ses documents."""

    documents = OnboardingDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = OnboardingStep
        fields = [
            "id",
            "title",
            "description",
            "step_type",
            "order",
            "is_mandatory",
            "duration_minutes",
            "content_url",
            "documents",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class OnboardingTemplateSerializer(serializers.ModelSerializer):
    """Serializer complet d'un template avec ses étapes."""

    steps = OnboardingStepSerializer(many=True, read_only=True)
    steps_count = serializers.IntegerField(source="steps.count", read_only=True)

    class Meta:
        model = OnboardingTemplate
        fields = [
            "id",
            "title",
            "description",
            "is_active",
            "steps",
            "steps_count",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]


class OnboardingTemplateListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour la liste des templates (sans étapes détaillées)."""

    steps_count = serializers.IntegerField(source="steps.count", read_only=True)

    class Meta:
        model = OnboardingTemplate
        fields = [
            "id",
            "title",
            "description",
            "is_active",
            "steps_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StepCompletionSerializer(serializers.ModelSerializer):
    """Serializer d'une complétion d'étape."""

    step_title = serializers.CharField(source="step.title", read_only=True)

    class Meta:
        model = StepCompletion
        fields = ["id", "step", "step_title", "completed_at", "note"]
        read_only_fields = ["id", "completed_at"]


class OnboardingAssignmentSerializer(serializers.ModelSerializer):
    """Serializer d'un assignment avec progression."""

    template = OnboardingTemplateSerializer(read_only=True)
    completions = StepCompletionSerializer(many=True, read_only=True)
    progress_percentage = serializers.IntegerField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    user_full_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = OnboardingAssignment
        fields = [
            "id",
            "user",
            "user_full_name",
            "template",
            "assigned_by",
            "due_date",
            "assigned_at",
            "completions",
            "progress_percentage",
            "is_completed",
        ]
        read_only_fields = ["id", "assigned_at", "assigned_by"]


class AssignmentCreateSerializer(serializers.ModelSerializer):
    """Serializer pour créer un assignment (manager/admin)."""

    class Meta:
        model = OnboardingAssignment
        fields = ["user", "template", "due_date"]


class CompleteStepSerializer(serializers.Serializer):
    """Serializer pour valider une étape."""

    note = serializers.CharField(required=False, allow_blank=True, default="")

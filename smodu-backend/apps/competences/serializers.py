"""Serializers du module compétences."""

from rest_framework import serializers
from .models import (
    CompetenceCategory,
    Competence,
    CompetenceAcquisition,
    CompetenceMatrix,
    MatrixCompetenceEntry,
)


class CompetenceCategorySerializer(serializers.ModelSerializer):
    competences_count = serializers.IntegerField(
        source="competences.count", read_only=True
    )

    class Meta:
        model = CompetenceCategory
        fields = [
            "id",
            "name",
            "description",
            "color",
            "competences_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CompetenceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Competence
        fields = [
            "id",
            "category",
            "category_name",
            "name",
            "description",
            "level_required",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CompetenceAcquisitionSerializer(serializers.ModelSerializer):
    """Acquisition d'une compétence — lecture."""

    competence_name = serializers.CharField(source="competence.name", read_only=True)
    category_name = serializers.CharField(
        source="competence.category.name", read_only=True
    )
    level_required = serializers.IntegerField(
        source="competence.level_required", read_only=True
    )
    is_validated = serializers.BooleanField(read_only=True)
    validated_by_name = serializers.CharField(
        source="validated_by.get_full_name", read_only=True, default=None
    )

    class Meta:
        model = CompetenceAcquisition
        fields = [
            "id",
            "user",
            "competence",
            "competence_name",
            "category_name",
            "level",
            "level_required",
            "is_validated",
            "source",
            "validated_by",
            "validated_by_name",
            "notes",
            "acquired_at",
            "updated_at",
        ]
        read_only_fields = ["id", "acquired_at", "updated_at"]


class CompetenceAcquisitionUpdateSerializer(serializers.ModelSerializer):
    """Mettre à jour le niveau d'une compétence (formateur/admin)."""

    class Meta:
        model = CompetenceAcquisition
        fields = ["level", "source", "notes"]


class MatrixEntrySerializer(serializers.ModelSerializer):
    competence = CompetenceSerializer(read_only=True)
    competence_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = MatrixCompetenceEntry
        fields = ["id", "competence", "competence_id", "target_level"]
        read_only_fields = ["id"]


class CompetenceMatrixSerializer(serializers.ModelSerializer):
    entries = MatrixEntrySerializer(
        source="matrixcompetenceentry_set", many=True, read_only=True
    )

    class Meta:
        model = CompetenceMatrix
        fields = [
            "id",
            "name",
            "description",
            "target_role",
            "entries",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]


class UserCompetenceProfileSerializer(serializers.Serializer):
    """
    Profil complet des compétences d'un utilisateur :
    acquisitions + gap analysis vs une matrice cible.
    """

    user_id = serializers.UUIDField()
    full_name = serializers.CharField()
    total_competences = serializers.IntegerField()
    validated_competences = serializers.IntegerField()
    validation_rate = serializers.FloatField()
    acquisitions = CompetenceAcquisitionSerializer(many=True)

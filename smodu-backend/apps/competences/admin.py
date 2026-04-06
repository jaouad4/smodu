"""Admin du module compétences."""

from django.contrib import admin
from .models import (
    CompetenceCategory,
    Competence,
    CompetenceAcquisition,
    CompetenceMatrix,
    MatrixCompetenceEntry,
)


class CompetenceInline(admin.TabularInline):
    model = Competence
    extra = 1
    fields = ["name", "level_required", "is_active"]


class MatrixEntryInline(admin.TabularInline):
    model = MatrixCompetenceEntry
    extra = 1
    fields = ["competence", "target_level"]


@admin.register(CompetenceCategory)
class CompetenceCategoryAdmin(admin.ModelAdmin):
    inlines = [CompetenceInline]
    list_display = ["name", "color", "created_at"]
    search_fields = ["name"]


@admin.register(Competence)
class CompetenceAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "level_required", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["name"]
    filter_horizontal = ["related_courses", "related_quizzes"]


@admin.register(CompetenceAcquisition)
class CompetenceAcquisitionAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "competence",
        "level",
        "source",
        "validated_by",
        "updated_at",
    ]
    list_filter = ["source", "competence__category"]
    search_fields = ["user__email", "competence__name"]


@admin.register(CompetenceMatrix)
class CompetenceMatrixAdmin(admin.ModelAdmin):
    inlines = [MatrixEntryInline]
    list_display = ["name", "target_role", "created_by", "created_at"]
    search_fields = ["name", "target_role"]

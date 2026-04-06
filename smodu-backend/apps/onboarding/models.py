"""Modèles du module onboarding : templates, étapes, assignments, documents."""

import uuid
from django.db import models
from apps.users.models import CustomUser


class StepType(models.TextChoices):
    """Types d'étapes d'onboarding supportés."""

    DOCUMENT_READ = "DOCUMENT_READ", "Lecture de document"
    TASK_COMPLETE = "TASK_COMPLETE", "Tâche à compléter"
    VIDEO_WATCH = "VIDEO_WATCH", "Vidéo à regarder"
    FORM_FILL = "FORM_FILL", "Formulaire à remplir"


class OnboardingTemplate(models.Model):
    """
    Modèle de parcours d'accueil réutilisable.
    Créé par un admin/formateur, assigné à plusieurs apprenants.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_templates",
        verbose_name="Créé par",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Template d'onboarding"
        verbose_name_plural = "Templates d'onboarding"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class OnboardingStep(models.Model):
    """Étape individuelle d'un template d'onboarding."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        OnboardingTemplate,
        on_delete=models.CASCADE,
        related_name="steps",
        verbose_name="Template",
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    step_type = models.CharField(
        max_length=20,
        choices=StepType.choices,
        default=StepType.TASK_COMPLETE,
        verbose_name="Type d'étape",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    is_mandatory = models.BooleanField(default=True, verbose_name="Obligatoire")
    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Durée estimée (minutes)",
    )
    content_url = models.URLField(blank=True, verbose_name="Lien vers le contenu")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Étape d'onboarding"
        verbose_name_plural = "Étapes d'onboarding"
        ordering = ["order"]
        unique_together = [["template", "order"]]

    def __str__(self):
        return f"{self.template.title} — Étape {self.order}: {self.title}"


class OnboardingDocument(models.Model):
    """Document attaché à une étape d'onboarding."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    step = models.ForeignKey(
        OnboardingStep,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Étape",
    )
    title = models.CharField(max_length=200, verbose_name="Titre du document")
    file = models.FileField(upload_to="onboarding/documents/", verbose_name="Fichier")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Document d'onboarding"
        verbose_name_plural = "Documents d'onboarding"

    def __str__(self):
        return f"{self.title} ({self.step.title})"


class OnboardingAssignment(models.Model):
    """Assignation d'un template d'onboarding à un utilisateur."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="onboarding_assignments",
        verbose_name="Apprenant",
    )
    template = models.ForeignKey(
        OnboardingTemplate,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="Template",
    )
    assigned_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assigned_onboardings",
        verbose_name="Assigné par",
    )
    due_date = models.DateField(null=True, blank=True, verbose_name="Date limite")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Assignment d'onboarding"
        verbose_name_plural = "Assignments d'onboarding"
        unique_together = [["user", "template"]]

    def __str__(self):
        return f"{self.user.get_full_name()} → {self.template.title}"

    @property
    def progress_percentage(self):
        """Calcule le % d'avancement de l'apprenant sur ce parcours."""
        total = self.template.steps.count()
        if total == 0:
            return 0
        completed = StepCompletion.objects.filter(
            assignment=self,
        ).count()
        return round((completed / total) * 100)

    @property
    def is_completed(self):
        """Retourne True si toutes les étapes obligatoires sont complétées."""
        mandatory_steps = self.template.steps.filter(is_mandatory=True)
        completed_ids = StepCompletion.objects.filter(
            assignment=self,
        ).values_list("step_id", flat=True)
        return all(step.id in completed_ids for step in mandatory_steps)


class StepCompletion(models.Model):
    """Validation d'une étape par un apprenant."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(
        OnboardingAssignment,
        on_delete=models.CASCADE,
        related_name="completions",
        verbose_name="Assignment",
    )
    step = models.ForeignKey(
        OnboardingStep,
        on_delete=models.CASCADE,
        related_name="completions",
        verbose_name="Étape",
    )
    completed_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, verbose_name="Note / commentaire")

    class Meta:
        verbose_name = "Complétion d'étape"
        verbose_name_plural = "Complétions d'étapes"
        unique_together = [["assignment", "step"]]

    def __str__(self):
        return f"{self.assignment.user.get_full_name()} ✓ {self.step.title}"

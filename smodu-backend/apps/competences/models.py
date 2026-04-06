"""Modèles du module compétences : référentiel, niveaux, acquisitions."""

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.models import CustomUser
from apps.formation.models import Course
from apps.evaluations.models import Quiz


class CompetenceCategory(models.Model):
    """Catégorie de compétences (ex: Odoo Comptabilité, Odoo Ventes...)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7, default="#01696f", verbose_name="Couleur hex"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie de compétence"
        verbose_name_plural = "Catégories de compétences"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Competence(models.Model):
    """
    Compétence individuelle du référentiel Odoo ERP.
    Ex : 'Configurer un plan comptable', 'Créer un devis Odoo Ventes'
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        CompetenceCategory,
        on_delete=models.CASCADE,
        related_name="competences",
        verbose_name="Catégorie",
    )
    name = models.CharField(max_length=200, verbose_name="Intitulé")
    description = models.TextField(blank=True)
    level_required = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Niveau requis (1-5)",
    )
    related_courses = models.ManyToManyField(
        Course,
        blank=True,
        related_name="competences",
        verbose_name="Cours liés",
    )
    related_quizzes = models.ManyToManyField(
        Quiz,
        blank=True,
        related_name="competences",
        verbose_name="Quiz liés",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Compétence"
        verbose_name_plural = "Compétences"
        ordering = ["category__name", "name"]

    def __str__(self):
        return f"[{self.category.name}] {self.name}"


class CompetenceAcquisition(models.Model):
    """
    Niveau d'acquisition d'une compétence par un utilisateur.
    Mis à jour automatiquement ou validé manuellement par un formateur.
    """

    class AcquisitionSource(models.TextChoices):
        QUIZ = "QUIZ", "Résultat de quiz"
        MANUAL = "MANUAL", "Validation manuelle"
        COURSE_COMPLETION = "COURSE_COMPLETION", "Fin de cours"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="competence_acquisitions",
        verbose_name="Utilisateur",
    )
    competence = models.ForeignKey(
        Competence,
        on_delete=models.CASCADE,
        related_name="acquisitions",
        verbose_name="Compétence",
    )
    level = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="Niveau acquis (0-5)",
    )
    source = models.CharField(
        max_length=20,
        choices=AcquisitionSource.choices,
        default=AcquisitionSource.MANUAL,
        verbose_name="Source d'acquisition",
    )
    validated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="validated_competences",
        verbose_name="Validé par",
    )
    notes = models.TextField(blank=True, verbose_name="Commentaires")
    acquired_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Acquisition de compétence"
        verbose_name_plural = "Acquisitions de compétences"
        unique_together = [["user", "competence"]]
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.competence.name} (niv. {self.level}/5)"

    @property
    def is_validated(self):
        """Compétence atteinte si niveau acquis >= niveau requis."""
        return self.level >= self.competence.level_required


class CompetenceMatrix(models.Model):
    """
    Matrice de compétences attendues pour un rôle/poste.
    Permet de comparer le profil réel vs attendu.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nom de la matrice")
    description = models.TextField(blank=True)
    target_role = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Rôle cible",
        help_text="Ex : Consultant Odoo Junior, Chef de Projet Odoo",
    )
    competences = models.ManyToManyField(
        Competence,
        through="MatrixCompetenceEntry",
        related_name="matrices",
        verbose_name="Compétences",
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_matrices",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Matrice de compétences"
        verbose_name_plural = "Matrices de compétences"

    def __str__(self):
        return self.name


class MatrixCompetenceEntry(models.Model):
    """Entrée dans une matrice : compétence + niveau cible."""

    matrix = models.ForeignKey(CompetenceMatrix, on_delete=models.CASCADE)
    competence = models.ForeignKey(Competence, on_delete=models.CASCADE)
    target_level = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Niveau cible",
    )

    class Meta:
        unique_together = [["matrix", "competence"]]
        verbose_name = "Entrée matrice"

    def __str__(self):
        return (
            f"{self.matrix.name} — {self.competence.name} (cible: {self.target_level})"
        )

"""Modèles du module formation : cours, modules, leçons, inscriptions, progression."""

import uuid
from django.db import models
from apps.users.models import CustomUser


class DifficultyLevel(models.TextChoices):
    BEGINNER = "BEGINNER", "Débutant"
    INTERMEDIATE = "INTERMEDIATE", "Intermédiaire"
    ADVANCED = "ADVANCED", "Avancé"


class ContentType(models.TextChoices):
    VIDEO = "VIDEO", "Vidéo"
    TEXT = "TEXT", "Texte / Article"
    INTERACTIVE = "INTERACTIVE", "Interactif"
    EXERCISE = "EXERCISE", "Exercice pratique"
    WEBINAR = "WEBINAR", "Webinaire"


class Course(models.Model):
    """
    Cours de formation Odoo ERP.
    Contient plusieurs modules, eux-mêmes composés de leçons.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Titre")
    slug = models.SlugField(unique=True, max_length=220, verbose_name="Slug URL")
    description = models.TextField(blank=True, verbose_name="Description")
    difficulty = models.CharField(
        max_length=15,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.BEGINNER,
        verbose_name="Niveau",
    )
    thumbnail = models.ImageField(
        upload_to="formation/thumbnails/",
        null=True,
        blank=True,
        verbose_name="Image de couverture",
    )
    duration_hours = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=0,
        verbose_name="Durée totale (heures)",
    )
    is_published = models.BooleanField(default=False, verbose_name="Publié")
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_courses",
        verbose_name="Créé par",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def enrollments_count(self):
        return self.enrollments.count()

    @property
    def modules_count(self):
        return self.modules.count()


class CourseModule(models.Model):
    """Module (chapitre) d'un cours."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules",
        verbose_name="Cours",
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        ordering = ["order"]
        unique_together = [["course", "order"]]

    def __str__(self):
        return f"{self.course.title} — Module {self.order}: {self.title}"


class Lesson(models.Model):
    """Leçon individuelle dans un module."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(
        CourseModule,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Module",
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    content_type = models.CharField(
        max_length=15,
        choices=ContentType.choices,
        default=ContentType.TEXT,
        verbose_name="Type de contenu",
    )
    content = models.TextField(blank=True, verbose_name="Contenu texte")
    content_url = models.URLField(blank=True, verbose_name="URL externe (vidéo, lien)")
    duration_minutes = models.PositiveIntegerField(
        default=0, verbose_name="Durée (min)"
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    is_free_preview = models.BooleanField(default=False, verbose_name="Aperçu gratuit")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Leçon"
        verbose_name_plural = "Leçons"
        ordering = ["order"]
        unique_together = [["module", "order"]]

    def __str__(self):
        return f"{self.module.title} — Leçon {self.order}: {self.title}"


class CourseEnrollment(models.Model):
    """Inscription d'un apprenant à un cours."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Apprenant",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Cours",
    )
    enrolled_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_enrollments",
        verbose_name="Inscrit par",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True, verbose_name="Date limite")
    completed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Terminé le"
    )

    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        unique_together = [["user", "course"]]
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.user.get_full_name()} → {self.course.title}"

    @property
    def progress_percentage(self):
        """Calcule le % de leçons complétées."""
        total = Lesson.objects.filter(module__course=self.course).count()
        if total == 0:
            return 0
        completed = LessonProgress.objects.filter(
            enrollment=self, is_completed=True
        ).count()
        return round((completed / total) * 100)


class LessonProgress(models.Model):
    """Progression d'un apprenant sur une leçon."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.ForeignKey(
        CourseEnrollment,
        on_delete=models.CASCADE,
        related_name="lesson_progresses",
        verbose_name="Inscription",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="progresses",
        verbose_name="Leçon",
    )
    is_completed = models.BooleanField(default=False, verbose_name="Complétée")
    time_spent_minutes = models.PositiveIntegerField(
        default=0, verbose_name="Temps passé (min)"
    )
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Progression leçon"
        verbose_name_plural = "Progressions leçons"
        unique_together = [["enrollment", "lesson"]]

    def __str__(self):
        status = "✓" if self.is_completed else "○"
        return f"{status} {self.enrollment.user.get_full_name()} — {self.lesson.title}"

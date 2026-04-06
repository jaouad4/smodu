"""Modèles du module évaluations : quiz, questions, réponses, tentatives."""

import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.models import CustomUser
from apps.formation.models import Course, Lesson


class QuizType(models.TextChoices):
    PRE_ASSESSMENT = "PRE_ASSESSMENT", "Évaluation initiale"
    POST_ASSESSMENT = "POST_ASSESSMENT", "Évaluation finale"
    CHAPTER_QUIZ = "CHAPTER_QUIZ", "Quiz de chapitre"
    CERTIFICATION = "CERTIFICATION", "Certification"


class QuestionType(models.TextChoices):
    SINGLE_CHOICE = "SINGLE_CHOICE", "Choix unique"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE", "Choix multiple"
    TRUE_FALSE = "TRUE_FALSE", "Vrai / Faux"
    SHORT_TEXT = "SHORT_TEXT", "Texte court (corrigé manuellement)"


class Quiz(models.Model):
    """Quiz lié à un cours ou une leçon."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True)
    quiz_type = models.CharField(
        max_length=20,
        choices=QuizType.choices,
        default=QuizType.CHAPTER_QUIZ,
        verbose_name="Type",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="quizzes",
        verbose_name="Cours associé",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="quizzes",
        verbose_name="Leçon associée",
    )
    passing_score = models.PositiveIntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Score de réussite (%)",
    )
    time_limit_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Limite de temps (min)",
    )
    max_attempts = models.PositiveIntegerField(
        default=3,
        verbose_name="Tentatives max (0 = illimité)",
    )
    shuffle_questions = models.BooleanField(
        default=True, verbose_name="Mélanger les questions"
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_quizzes",
        verbose_name="Créé par",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quiz"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def questions_count(self):
        return self.questions.count()


class Question(models.Model):
    """Question d'un quiz."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Quiz",
    )
    text = models.TextField(verbose_name="Énoncé de la question")
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE_CHOICE,
        verbose_name="Type de question",
    )
    points = models.PositiveIntegerField(default=1, verbose_name="Points")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    explanation = models.TextField(
        blank=True,
        verbose_name="Explication (affiché après réponse)",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ["order"]

    def __str__(self):
        return f"[{self.quiz.title}] Q{self.order}: {self.text[:60]}"


class AnswerChoice(models.Model):
    """Choix de réponse pour une question à choix."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
        verbose_name="Question",
    )
    text = models.CharField(max_length=500, verbose_name="Texte du choix")
    is_correct = models.BooleanField(default=False, verbose_name="Correct")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")

    class Meta:
        verbose_name = "Choix de réponse"
        verbose_name_plural = "Choix de réponses"
        ordering = ["order"]

    def __str__(self):
        marker = "✓" if self.is_correct else "✗"
        return f"{marker} {self.text[:60]}"


class QuizAttempt(models.Model):
    """Tentative d'un apprenant sur un quiz."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
        verbose_name="Apprenant",
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Quiz",
    )
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Score obtenu (%)",
    )
    is_passed = models.BooleanField(null=True, blank=True, verbose_name="Réussi")
    attempt_number = models.PositiveIntegerField(
        default=1, verbose_name="Numéro de tentative"
    )

    class Meta:
        verbose_name = "Tentative de quiz"
        verbose_name_plural = "Tentatives de quiz"
        ordering = ["-started_at"]
        unique_together = [["user", "quiz", "attempt_number"]]

    def __str__(self):
        status = "✓" if self.is_passed else "✗"
        return f"{status} {self.user.get_full_name()} — {self.quiz.title} (tentative {self.attempt_number})"

    def calculate_score(self):
        """Calcule et enregistre le score automatiquement."""
        answers = self.answers.select_related("question").prefetch_related(
            "selected_choices"
        )
        total_points = sum(a.question.points for a in answers)
        if total_points == 0:
            return 0

        earned_points = 0
        for answer in answers:
            q = answer.question
            if q.question_type == QuestionType.SHORT_TEXT:
                continue  # corrigé manuellement
            correct_ids = set(
                q.choices.filter(is_correct=True).values_list("id", flat=True)
            )
            selected_ids = set(answer.selected_choices.values_list("id", flat=True))
            if correct_ids == selected_ids:
                earned_points += q.points

        self.score = round((earned_points / total_points) * 100, 2)
        self.is_passed = self.score >= self.quiz.passing_score
        self.save(update_fields=["score", "is_passed", "submitted_at"])
        return self.score


class QuestionAnswer(models.Model):
    """Réponse d'un apprenant à une question lors d'une tentative."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Tentative",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="user_answers",
        verbose_name="Question",
    )
    selected_choices = models.ManyToManyField(
        AnswerChoice,
        blank=True,
        related_name="user_answers",
        verbose_name="Choix sélectionnés",
    )
    text_answer = models.TextField(
        blank=True,
        verbose_name="Réponse texte libre",
    )
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Réponse"
        verbose_name_plural = "Réponses"
        unique_together = [["attempt", "question"]]

    def __str__(self):
        return (
            f"Réponse de {self.attempt.user.get_full_name()} à Q{self.question.order}"
        )

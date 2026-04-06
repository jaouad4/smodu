"""Admin du module évaluations."""

from django.contrib import admin
from .models import Quiz, Question, AnswerChoice, QuizAttempt, QuestionAnswer


class AnswerChoiceInline(admin.TabularInline):
    model = AnswerChoice
    extra = 2
    fields = ["text", "is_correct", "order"]


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True
    fields = ["text", "question_type", "points", "order", "explanation"]


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = [
        "title",
        "quiz_type",
        "passing_score",
        "max_attempts",
        "is_active",
        "created_by",
    ]
    list_filter = ["quiz_type", "is_active"]
    search_fields = ["title"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerChoiceInline]
    list_display = ["text", "quiz", "question_type", "points", "order"]
    list_filter = ["question_type", "quiz"]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "quiz",
        "score",
        "is_passed",
        "attempt_number",
        "submitted_at",
    ]
    list_filter = ["is_passed", "quiz"]
    search_fields = ["user__email"]
    readonly_fields = ["score", "is_passed", "submitted_at", "started_at"]

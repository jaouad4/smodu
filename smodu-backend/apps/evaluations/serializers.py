"""Serializers du module évaluations."""

from rest_framework import serializers
from .models import Quiz, Question, AnswerChoice, QuizAttempt, QuestionAnswer


class AnswerChoiceSerializer(serializers.ModelSerializer):
    """Choix de réponse — is_correct masqué pour les apprenants."""

    class Meta:
        model = AnswerChoice
        fields = ["id", "text", "order"]


class AnswerChoiceAdminSerializer(serializers.ModelSerializer):
    """Choix de réponse avec is_correct (admin/formateur uniquement)."""

    class Meta:
        model = AnswerChoice
        fields = ["id", "text", "is_correct", "order"]


class QuestionSerializer(serializers.ModelSerializer):
    """Question sans les bonnes réponses (vue apprenant)."""

    choices = AnswerChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "question_type",
            "points",
            "order",
            "choices",
        ]
        read_only_fields = ["id"]


class QuestionAdminSerializer(serializers.ModelSerializer):
    """Question avec les bonnes réponses (vue admin/formateur)."""

    choices = AnswerChoiceAdminSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "question_type",
            "points",
            "order",
            "explanation",
            "choices",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class QuizListSerializer(serializers.ModelSerializer):
    """Quiz — liste allégée."""

    questions_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "quiz_type",
            "passing_score",
            "time_limit_minutes",
            "max_attempts",
            "questions_count",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class QuizDetailSerializer(serializers.ModelSerializer):
    """Quiz complet avec questions (pour passer le quiz)."""

    questions = QuestionSerializer(many=True, read_only=True)
    questions_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "quiz_type",
            "passing_score",
            "time_limit_minutes",
            "max_attempts",
            "shuffle_questions",
            "is_active",
            "questions",
            "questions_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class QuestionAnswerSubmitSerializer(serializers.Serializer):
    """Réponse à une question lors d'une soumission."""

    question_id = serializers.UUIDField()
    selected_choice_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list,
    )
    text_answer = serializers.CharField(required=False, allow_blank=True, default="")


class QuizSubmitSerializer(serializers.Serializer):
    """Soumission complète d'un quiz."""

    answers = QuestionAnswerSubmitSerializer(many=True)


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Résultat d'une tentative."""

    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    user_full_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "user",
            "user_full_name",
            "quiz",
            "quiz_title",
            "started_at",
            "submitted_at",
            "score",
            "is_passed",
            "attempt_number",
        ]
        read_only_fields = fields

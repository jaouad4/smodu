"""Vues du module évaluations."""

from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsTrainerOrAdmin, IsManagerOrAdmin
from .models import Quiz, QuizAttempt, QuestionAnswer, AnswerChoice, Question
from .serializers import (
    QuizListSerializer,
    QuizDetailSerializer,
    QuizSubmitSerializer,
    QuizAttemptSerializer,
)


class QuizListView(generics.ListAPIView):
    """GET /api/evaluations/quizzes/ — liste des quiz actifs."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuizListSerializer
    queryset = Quiz.objects.filter(is_active=True)


class QuizDetailView(generics.RetrieveAPIView):
    """GET /api/evaluations/quizzes/{id}/ — détail quiz + questions."""

    permission_classes = [permissions.IsAuthenticated]
    queryset = Quiz.objects.filter(is_active=True).prefetch_related(
        "questions__choices"
    )
    serializer_class = QuizDetailSerializer


class StartQuizView(APIView):
    """POST /api/evaluations/quizzes/{id}/start/ — démarrer une tentative."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        quiz = generics.get_object_or_404(Quiz, pk=pk, is_active=True)

        # Vérifier le nombre de tentatives
        attempts_count = QuizAttempt.objects.filter(
            user=request.user, quiz=quiz
        ).count()

        if quiz.max_attempts > 0 and attempts_count >= quiz.max_attempts:
            return Response(
                {
                    "detail": f"Nombre maximum de tentatives atteint ({quiz.max_attempts})."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            attempt_number=attempts_count + 1,
        )

        return Response(
            {
                "attempt_id": str(attempt.id),
                "attempt_number": attempt.attempt_number,
                "started_at": attempt.started_at,
                "time_limit_minutes": quiz.time_limit_minutes,
            },
            status=status.HTTP_201_CREATED,
        )


class SubmitQuizView(APIView):
    """POST /api/evaluations/attempts/{id}/submit/ — soumettre les réponses."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        attempt = generics.get_object_or_404(QuizAttempt, pk=pk, user=request.user)

        if attempt.submitted_at:
            return Response(
                {"detail": "Cette tentative a déjà été soumise."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = QuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for answer_data in serializer.validated_data["answers"]:
            question = generics.get_object_or_404(
                Question, pk=answer_data["question_id"], quiz=attempt.quiz
            )

            question_answer, _ = QuestionAnswer.objects.get_or_create(
                attempt=attempt,
                question=question,
                defaults={"text_answer": answer_data.get("text_answer", "")},
            )

            if answer_data.get("selected_choice_ids"):
                choices = AnswerChoice.objects.filter(
                    id__in=answer_data["selected_choice_ids"],
                    question=question,
                )
                question_answer.selected_choices.set(choices)

        attempt.submitted_at = timezone.now()
        attempt.save(update_fields=["submitted_at"])
        attempt.calculate_score()

        return Response(
            {
                "score": attempt.score,
                "is_passed": attempt.is_passed,
                "passing_score": attempt.quiz.passing_score,
                "attempt_number": attempt.attempt_number,
            },
            status=status.HTTP_200_OK,
        )


class MyAttemptsView(generics.ListAPIView):
    """GET /api/evaluations/my-attempts/ — historique des tentatives."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuizAttemptSerializer

    def get_queryset(self):
        return (
            QuizAttempt.objects.filter(user=self.request.user)
            .select_related("quiz")
            .order_by("-started_at")
        )


class AllAttemptsView(generics.ListAPIView):
    """GET /api/evaluations/attempts/ — toutes les tentatives (manager/admin)."""

    permission_classes = [IsManagerOrAdmin]
    serializer_class = QuizAttemptSerializer

    def get_queryset(self):
        return QuizAttempt.objects.select_related("user", "quiz").order_by(
            "-started_at"
        )


class QuizAdminListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/evaluations/admin/quizzes/ — gestion quiz (formateur/admin)."""

    permission_classes = [IsTrainerOrAdmin]
    queryset = Quiz.objects.prefetch_related("questions__choices")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return QuizDetailSerializer
        return QuizListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

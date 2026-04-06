"""URLs du module évaluations."""

from django.urls import path
from .views import (
    QuizListView,
    QuizDetailView,
    StartQuizView,
    SubmitQuizView,
    MyAttemptsView,
    AllAttemptsView,
    QuizAdminListCreateView,
)

urlpatterns = [
    # Apprenant
    path("quizzes/", QuizListView.as_view(), name="quiz-list"),
    path("quizzes/<uuid:pk>/", QuizDetailView.as_view(), name="quiz-detail"),
    path("quizzes/<uuid:pk>/start/", StartQuizView.as_view(), name="quiz-start"),
    path("attempts/<uuid:pk>/submit/", SubmitQuizView.as_view(), name="quiz-submit"),
    path("my-attempts/", MyAttemptsView.as_view(), name="my-attempts"),
    # Manager / Admin
    path("attempts/", AllAttemptsView.as_view(), name="all-attempts"),
    path("admin/quizzes/", QuizAdminListCreateView.as_view(), name="quiz-admin"),
]

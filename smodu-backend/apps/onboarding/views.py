"""Vues du module onboarding."""

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsManagerOrAdmin, IsTrainerOrAdmin
from .models import (
    OnboardingTemplate,
    OnboardingStep,
    OnboardingAssignment,
    StepCompletion,
)
from .serializers import (
    OnboardingTemplateSerializer,
    OnboardingTemplateListSerializer,
    OnboardingAssignmentSerializer,
    AssignmentCreateSerializer,
    CompleteStepSerializer,
)


class MyOnboardingJourneyView(APIView):
    """GET /api/onboarding/my-journey/ — parcours de l'apprenant connecté."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        assignments = (
            OnboardingAssignment.objects.filter(user=request.user)
            .select_related("template")
            .prefetch_related(
                "template__steps__documents",
                "completions",
            )
        )
        serializer = OnboardingAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)


class CompleteStepView(APIView):
    """POST /api/onboarding/steps/{id}/complete/ — valider une étape."""

    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        step = get_object_or_404(OnboardingStep, pk=pk)

        # L'apprenant doit avoir un assignment actif pour ce template
        assignment = OnboardingAssignment.objects.filter(
            user=request.user,
            template=step.template,
        ).first()

        if not assignment:
            return Response(
                {"detail": "Aucun parcours actif trouvé pour cette étape."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CompleteStepSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        completion, created = StepCompletion.objects.get_or_create(
            assignment=assignment,
            step=step,
            defaults={"note": serializer.validated_data.get("note", "")},
        )

        if not created:
            return Response(
                {"detail": "Cette étape est déjà complétée."},
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "detail": "Étape complétée avec succès.",
                "progress_percentage": assignment.progress_percentage,
                "is_completed": assignment.is_completed,
            },
            status=status.HTTP_201_CREATED,
        )


class OnboardingTemplateListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/onboarding/templates/ — liste et création (admin/formateur)."""

    permission_classes = [IsTrainerOrAdmin]
    queryset = OnboardingTemplate.objects.prefetch_related("steps").order_by(
        "-created_at"
    )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OnboardingTemplateSerializer
        return OnboardingTemplateListSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class OnboardingTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/onboarding/templates/{id}/ — détail d'un template."""

    permission_classes = [IsTrainerOrAdmin]
    queryset = OnboardingTemplate.objects.prefetch_related("steps__documents")
    serializer_class = OnboardingTemplateSerializer


class OnboardingAssignmentListView(generics.ListCreateAPIView):
    """GET/POST /api/onboarding/assignments/ — suivi global (manager)."""

    permission_classes = [IsManagerOrAdmin]

    def get_queryset(self):
        return (
            OnboardingAssignment.objects.select_related(
                "user", "template", "assigned_by"
            )
            .prefetch_related("completions")
            .order_by("-assigned_at")
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AssignmentCreateSerializer
        return OnboardingAssignmentSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

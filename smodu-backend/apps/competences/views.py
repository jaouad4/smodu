"""Vues du module compétences."""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import CustomUser
from apps.users.permissions import IsTrainerOrAdmin, IsManagerOrAdmin, IsOwnerOrAdmin
from .models import (
    CompetenceCategory,
    Competence,
    CompetenceAcquisition,
    CompetenceMatrix,
)
from .serializers import (
    CompetenceCategorySerializer,
    CompetenceSerializer,
    CompetenceAcquisitionSerializer,
    CompetenceAcquisitionUpdateSerializer,
    CompetenceMatrixSerializer,
    UserCompetenceProfileSerializer,
)


class CompetenceCategoryListView(generics.ListCreateAPIView):
    """GET/POST /api/competences/categories/"""

    permission_classes = [permissions.IsAuthenticated]
    queryset = CompetenceCategory.objects.all()
    serializer_class = CompetenceCategorySerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsTrainerOrAdmin()]
        return [permissions.IsAuthenticated()]


class CompetenceListView(generics.ListCreateAPIView):
    """GET/POST /api/competences/ — référentiel complet."""

    permission_classes = [permissions.IsAuthenticated]
    queryset = Competence.objects.select_related("category").filter(is_active=True)
    serializer_class = CompetenceSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsTrainerOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__id=category)
        return qs


class MyCompetencesView(APIView):
    """GET /api/competences/me/ — profil compétences de l'utilisateur connecté."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        acquisitions = CompetenceAcquisition.objects.filter(
            user=request.user
        ).select_related("competence__category", "validated_by")
        validated = [a for a in acquisitions if a.is_validated]
        total = acquisitions.count()

        data = {
            "user_id": request.user.id,
            "full_name": request.user.get_full_name(),
            "total_competences": total,
            "validated_competences": len(validated),
            "validation_rate": (
                round(len(validated) / total * 100, 1) if total > 0 else 0
            ),
            "acquisitions": acquisitions,
        }
        return Response(UserCompetenceProfileSerializer(data).data)


class UserCompetencesView(APIView):
    """GET /api/competences/users/{id}/ — profil compétences d'un utilisateur (manager/admin)."""

    permission_classes = [IsManagerOrAdmin]

    def get(self, request, pk):
        user = generics.get_object_or_404(CustomUser, pk=pk)
        acquisitions = CompetenceAcquisition.objects.filter(user=user).select_related(
            "competence__category", "validated_by"
        )
        validated = [a for a in acquisitions if a.is_validated]
        total = acquisitions.count()

        data = {
            "user_id": user.id,
            "full_name": user.get_full_name(),
            "total_competences": total,
            "validated_competences": len(validated),
            "validation_rate": (
                round(len(validated) / total * 100, 1) if total > 0 else 0
            ),
            "acquisitions": acquisitions,
        }
        return Response(UserCompetenceProfileSerializer(data).data)


class CompetenceAcquisitionUpdateView(generics.UpdateAPIView):
    """PATCH /api/competences/acquisitions/{id}/ — valider/modifier une compétence."""

    permission_classes = [IsTrainerOrAdmin]
    queryset = CompetenceAcquisition.objects.all()
    serializer_class = CompetenceAcquisitionUpdateSerializer

    def perform_update(self, serializer):
        serializer.save(validated_by=self.request.user)


class CompetenceMatrixListCreateView(generics.ListCreateAPIView):
    """GET/POST /api/competences/matrices/"""

    permission_classes = [IsTrainerOrAdmin]
    queryset = CompetenceMatrix.objects.prefetch_related(
        "matrixcompetenceentry_set__competence__category"
    )
    serializer_class = CompetenceMatrixSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CompetenceMatrixDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/competences/matrices/{id}/"""

    permission_classes = [IsTrainerOrAdmin]
    queryset = CompetenceMatrix.objects.prefetch_related(
        "matrixcompetenceentry_set__competence__category"
    )
    serializer_class = CompetenceMatrixSerializer

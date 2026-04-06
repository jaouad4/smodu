"""Vues pour l'authentification et la gestion des utilisateurs."""

from django.db import transaction
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser, UserProfile
from .permissions import IsAdmin, IsOwnerOrAdmin
from .serializers import (
    SMODUTokenObtainPairSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)


class SMODUTokenObtainPairView(TokenObtainPairView):
    """Login — retourne access + refresh token enrichis."""

    serializer_class = SMODUTokenObtainPairSerializer


class LogoutView(APIView):
    """Blacklist le refresh token (déconnexion)."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Déconnexion réussie."}, status=status.HTTP_205_RESET_CONTENT
            )
        except Exception:
            return Response(
                {"detail": "Token invalide."}, status=status.HTTP_400_BAD_REQUEST
            )


class MeView(generics.RetrieveUpdateAPIView):
    """Profil de l'utilisateur connecté — GET et PUT."""

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserSerializer


class UserListCreateView(generics.ListCreateAPIView):
    """Liste et création des utilisateurs (admin uniquement)."""

    permission_classes = [IsAdmin]
    queryset = CustomUser.objects.select_related("profile").order_by("-date_joined")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        user = serializer.save()
        UserProfile.objects.get_or_create(user=user)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, modification et désactivation (soft delete) d'un utilisateur."""

    permission_classes = [IsOwnerOrAdmin]
    queryset = CustomUser.objects.select_related("profile")

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        """Soft delete — désactive l'utilisateur sans le supprimer."""
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response(
            {"detail": f"Utilisateur {user.email} désactivé."},
            status=status.HTTP_200_OK,
        )

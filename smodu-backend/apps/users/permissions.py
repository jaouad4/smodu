"""Classes de permissions personnalisées par rôle SMODU."""

from rest_framework.permissions import BasePermission
from .models import Role


class IsAdmin(BasePermission):
    """Accès réservé aux administrateurs."""

    message = "Accès réservé aux administrateurs."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.ADMIN
        )


class IsManagerOrAdmin(BasePermission):
    """Accès réservé aux managers, RH et administrateurs."""

    message = "Accès réservé aux managers et administrateurs."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (Role.ADMIN, Role.MANAGER, Role.HR)
        )


class IsTrainerOrAdmin(BasePermission):
    """Accès réservé aux formateurs, référents Odoo et administrateurs."""

    message = "Accès réservé aux formateurs et administrateurs."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (Role.ADMIN, Role.TRAINER, Role.ODOO_REF)
        )


class IsLearner(BasePermission):
    """Accès réservé aux apprenants."""

    message = "Accès réservé aux apprenants."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.LEARNER
        )


class IsOwnerOrAdmin(BasePermission):
    """L'utilisateur ne peut accéder qu'à ses propres ressources (ou admin)."""

    message = "Vous ne pouvez accéder qu'à vos propres ressources."

    def has_object_permission(self, request, view, obj):
        if request.user.role == Role.ADMIN:
            return True
        if hasattr(obj, "user"):
            return obj.user == request.user
        return obj == request.user

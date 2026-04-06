"""URLs du module users."""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    SMODUTokenObtainPairView,
    LogoutView,
    MeView,
    UserListCreateView,
    UserDetailView,
)

urlpatterns = [
    # Auth
    path("login/", SMODUTokenObtainPairView.as_view(), name="auth-login"),
    path("refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
    # Gestion utilisateurs (admin)
    path("users/", UserListCreateView.as_view(), name="user-list-create"),
    path("users/<uuid:pk>/", UserDetailView.as_view(), name="user-detail"),
]

"""Vues du module notifications."""

from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification, NotificationPreferences
from .serializers import NotificationSerializer, NotificationPreferencesSerializer


class MyNotificationsView(generics.ListAPIView):
    """GET /api/notifications/ — notifications de l'utilisateur connecté."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        qs = Notification.objects.filter(recipient=self.request.user)
        unread_only = self.request.query_params.get("unread")
        if unread_only:
            qs = qs.filter(is_read=False)
        return qs


class UnreadCountView(APIView):
    """GET /api/notifications/unread-count/ — nombre de notifications non lues."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return Response({"unread_count": count})


class MarkReadView(APIView):
    """POST /api/notifications/{id}/read/ — marquer une notification comme lue."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        notification = generics.get_object_or_404(
            Notification, pk=pk, recipient=request.user
        )
        notification.mark_as_read()
        return Response({"detail": "Notification marquée comme lue."})


class MarkAllReadView(APIView):
    """POST /api/notifications/mark-all-read/ — tout marquer comme lu."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        now = timezone.now()
        updated = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True, read_at=now)
        return Response({"detail": f"{updated} notifications marquées comme lues."})


class NotificationPreferencesView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/notifications/preferences/ — préférences de l'utilisateur."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationPreferencesSerializer

    def get_object(self):
        prefs, _ = NotificationPreferences.objects.get_or_create(user=self.request.user)
        return prefs

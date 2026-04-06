"""URLs du module notifications."""

from django.urls import path
from .views import (
    MyNotificationsView,
    UnreadCountView,
    MarkReadView,
    MarkAllReadView,
    NotificationPreferencesView,
)

urlpatterns = [
    path("", MyNotificationsView.as_view(), name="notifications"),
    path("unread-count/", UnreadCountView.as_view(), name="notifications-unread-count"),
    path(
        "mark-all-read/", MarkAllReadView.as_view(), name="notifications-mark-all-read"
    ),
    path("<uuid:pk>/read/", MarkReadView.as_view(), name="notification-mark-read"),
    path(
        "preferences/",
        NotificationPreferencesView.as_view(),
        name="notification-preferences",
    ),
]

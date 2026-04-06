"""URLs du module dashboard."""

from django.urls import path
from .views import (
    LearnerDashboardView,
    ManagerDashboardView,
    LearnerReportView,
    LearnersListView,
)

urlpatterns = [
    path("me/", LearnerDashboardView.as_view(), name="dashboard-learner"),
    path("manager/", ManagerDashboardView.as_view(), name="dashboard-manager"),
    path("learners/", LearnersListView.as_view(), name="dashboard-learners-list"),
    path(
        "learners/<uuid:pk>/report/",
        LearnerReportView.as_view(),
        name="dashboard-learner-report",
    ),
]

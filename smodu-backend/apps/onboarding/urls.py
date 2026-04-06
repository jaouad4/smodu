"""URLs du module onboarding."""

from django.urls import path
from .views import (
    MyOnboardingJourneyView,
    CompleteStepView,
    OnboardingTemplateListCreateView,
    OnboardingTemplateDetailView,
    OnboardingAssignmentListView,
)

urlpatterns = [
    path(
        "my-journey/", MyOnboardingJourneyView.as_view(), name="onboarding-my-journey"
    ),
    path(
        "steps/<uuid:pk>/complete/",
        CompleteStepView.as_view(),
        name="onboarding-step-complete",
    ),
    path(
        "templates/",
        OnboardingTemplateListCreateView.as_view(),
        name="onboarding-templates",
    ),
    path(
        "templates/<uuid:pk>/",
        OnboardingTemplateDetailView.as_view(),
        name="onboarding-template-detail",
    ),
    path(
        "assignments/",
        OnboardingAssignmentListView.as_view(),
        name="onboarding-assignments",
    ),
]

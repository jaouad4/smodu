"""URLs du module compétences."""

from django.urls import path
from .views import (
    CompetenceCategoryListView,
    CompetenceListView,
    MyCompetencesView,
    UserCompetencesView,
    CompetenceAcquisitionUpdateView,
    CompetenceMatrixListCreateView,
    CompetenceMatrixDetailView,
)

urlpatterns = [
    path(
        "categories/",
        CompetenceCategoryListView.as_view(),
        name="competence-categories",
    ),
    path("", CompetenceListView.as_view(), name="competence-list"),
    path("me/", MyCompetencesView.as_view(), name="my-competences"),
    path("users/<uuid:pk>/", UserCompetencesView.as_view(), name="user-competences"),
    path(
        "acquisitions/<uuid:pk>/",
        CompetenceAcquisitionUpdateView.as_view(),
        name="acquisition-update",
    ),
    path("matrices/", CompetenceMatrixListCreateView.as_view(), name="matrix-list"),
    path(
        "matrices/<uuid:pk>/",
        CompetenceMatrixDetailView.as_view(),
        name="matrix-detail",
    ),
]

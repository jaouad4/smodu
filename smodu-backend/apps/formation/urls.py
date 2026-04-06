"""URLs du module formation."""

from django.urls import path
from .views import (
    CourseListView,
    CourseAdminListCreateView,
    CourseDetailView,
    MyCoursesView,
    EnrollmentListCreateView,
    LessonProgressView,
)

urlpatterns = [
    # Apprenant
    path("courses/", CourseListView.as_view(), name="course-list"),
    path("courses/<uuid:pk>/", CourseDetailView.as_view(), name="course-detail"),
    path("my-courses/", MyCoursesView.as_view(), name="my-courses"),
    path(
        "lessons/<uuid:pk>/progress/",
        LessonProgressView.as_view(),
        name="lesson-progress",
    ),
    # Admin / Formateur
    path(
        "admin/courses/", CourseAdminListCreateView.as_view(), name="course-admin-list"
    ),
    path("enrollments/", EnrollmentListCreateView.as_view(), name="enrollment-list"),
]

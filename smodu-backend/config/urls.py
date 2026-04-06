"""URLs racine du projet SMODU."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,  # ← corrigé (pas SwaggerUIView)
    SpectacularRedocView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # OpenAPI / Swagger
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Modules applicatifs
    path("api/auth/", include("apps.users.urls")),
    path("api/onboarding/", include("apps.onboarding.urls")),
    path("api/formation/", include("apps.formation.urls")),
    path("api/evaluations/", include("apps.evaluations.urls")),
    path("api/competences/", include("apps.competences.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
    # path("api/validation/", include("apps.validation.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

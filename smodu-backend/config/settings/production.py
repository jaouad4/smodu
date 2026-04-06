"""Settings de production — sécurité renforcée, pas de debug."""

from .base import *  # noqa: F401, F403

DEBUG = False

CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(  # noqa: F405
    ","
)
CORS_ALLOW_CREDENTIALS = True

# Sécurité HTTP
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

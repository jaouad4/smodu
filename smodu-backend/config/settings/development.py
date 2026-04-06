"""Settings de développement — hot reload, debug, logs détaillés."""

from .base import *  # noqa: F401, F403

DEBUG = True

# SECURITY WARNING: gardez ces valeurs uniquement en dev
SECRET_KEY = os.environ.get(  # noqa: F405
    "DJANGO_SECRET_KEY", "dev-secret-key-not-for-production-use-only"
)

ALLOWED_HOSTS = ["*"]

# CORS : React Vite en dev
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True

# Debug toolbar
INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa: F405
INTERNAL_IPS = ["127.0.0.1"]

# Email en console (pas d'envoi réel en dev)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Logs plus verbeux en dev
LOGGING["root"]["level"] = "DEBUG"  # noqa: F405

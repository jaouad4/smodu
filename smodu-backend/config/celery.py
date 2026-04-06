"""Configuration Celery pour SMODU."""

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("smodu")

# Lit la config depuis Django settings, préfixe CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodécouverte des tâches dans chaque app Django
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Tâche de test pour vérifier que Celery fonctionne."""
    print(f"Request: {self.request!r}")

# ─── Stage 1 : base commune ───────────────────────────
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dépendances système (psycopg2, Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ─── Stage 2 : développement ──────────────────────────
FROM base AS development

COPY requirements/base.txt requirements/development.txt ./requirements/
RUN pip install -r requirements/development.txt

COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ─── Stage 3 : builder (compilation des dépendances prod) ─
FROM base AS builder

COPY requirements/base.txt requirements/production.txt ./requirements/
RUN pip install --prefix=/install -r requirements/production.txt

# ─── Stage 4 : production (image finale minimale) ─────
FROM python:3.12-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copie uniquement les packages installés depuis le builder
COPY --from=builder /install /usr/local

COPY . .

# Collecte des fichiers statiques au build
RUN python manage.py collectstatic --noinput \
    --settings=config.settings.production || true

# Utilisateur non-root pour la sécurité
RUN addgroup --system smodu && adduser --system --ingroup smodu smodu
RUN chown -R smodu:smodu /app
USER smodu

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", \
    "--bind", "0.0.0.0:8000", \
    "--workers", "4", \
    "--timeout", "120", \
    "--access-logfile", "-"]
"""
Script de création des données de démo pour la présentation manager.
Exécuter : docker exec smodu_backend python create_demo_data.py
"""

import os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from apps.users.models import CustomUser, UserProfile, Role
from apps.competences.models import (
    CompetenceCategory,
    Competence,
    CompetenceAcquisition,
)

print("🧹 Nettoyage des données existantes...")
CompetenceAcquisition.objects.all().delete()
Competence.objects.all().delete()
CompetenceCategory.objects.all().delete()
UserProfile.objects.all().delete()
CustomUser.objects.filter(is_superuser=False).delete()

# ── USERS ──────────────────────────────────────────────────────
print("👤 Création des utilisateurs...")


def make_user(
    email, password, first_name, last_name, role, department, status, contract
):
    user, _ = CustomUser.objects.get_or_create(
        email=email,
        defaults=dict(
            first_name=first_name,
            last_name=last_name,
            role=role,
            department=department,
        ),
    )
    user.set_password(password)
    user.first_name = first_name
    user.last_name = last_name
    user.role = role
    user.department = department
    user.save()
    UserProfile.objects.update_or_create(
        user=user, defaults=dict(contract_type=contract, project_status=status)
    )
    return user


manager = make_user(
    email="manager@smodu.ma",
    password="Demo1234!",
    first_name="Karim",
    last_name="Benjelloun",
    role=Role.MANAGER,
    department="Consulting Odoo",
    status="VALIDATED",
    contract="CDI",
)
print(f"  ✓ {manager.get_full_name()} (MANAGER)")

learners_data = [
    dict(
        email="sara@smodu.ma",
        first_name="Sara",
        last_name="Amrani",
        department="CRM",
        status="TRAINING",
        contract="Stage",
    ),
    dict(
        email="youssef@smodu.ma",
        first_name="Youssef",
        last_name="El Fassi",
        department="Comptabilité",
        status="EVALUATION",
        contract="Alternance",
    ),
    dict(
        email="nadia@smodu.ma",
        first_name="Nadia",
        last_name="Tahiri",
        department="RH",
        status="ONBOARDING",
        contract="CDD",
    ),
    dict(
        email="mehdi@smodu.ma",
        first_name="Mehdi",
        last_name="Bouzid",
        department="Ventes",
        status="VALIDATED",
        contract="CDI",
    ),
]

learner_users = []
for l in learners_data:
    u = make_user(password="Demo1234!", role=Role.LEARNER, **l)
    learner_users.append(u)
    print(f"  ✓ {u.get_full_name()} ({l['status']})")

# ── COMPÉTENCES ────────────────────────────────────────────────
print("📊 Création des compétences...")

crm_cat = CompetenceCategory.objects.create(name="CRM Odoo", color="#006494")
ventes_cat = CompetenceCategory.objects.create(name="Ventes", color="#01696f")
compta_cat = CompetenceCategory.objects.create(name="Comptabilité", color="#da7101")

skills_data = [
    (crm_cat, "Gérer les leads et opportunités", 2),
    (crm_cat, "Configurer le pipeline de vente", 3),
    (ventes_cat, "Créer et valider un devis", 2),
    (ventes_cat, "Gérer les commandes clients", 3),
    (compta_cat, "Configurer le plan comptable", 3),
    (compta_cat, "Saisir des pièces comptables", 2),
]

competences = []
for cat, name, level in skills_data:
    c = Competence.objects.create(category=cat, name=name, level_required=level)
    competences.append(c)

sara, youssef, nadia, mehdi = learner_users

# Sara (TRAINING) : compétences CRM partielles
for i, c in enumerate(competences[:3]):
    CompetenceAcquisition.objects.create(
        user=sara, competence=c, level=i + 1, source="COURSE_COMPLETION"
    )

# Youssef (EVALUATION) : CRM avancé + ventes débutant
for i, c in enumerate(competences[:4]):
    CompetenceAcquisition.objects.create(
        user=youssef, competence=c, level=min(i + 2, 3), source="QUIZ"
    )

# Nadia (ONBOARDING) : aucune compétence encore — rien à insérer

# Mehdi (VALIDATED) : toutes compétences validées par le manager
for c in competences:
    CompetenceAcquisition.objects.create(
        user=mehdi, competence=c, level=4, source="MANUAL", validated_by=manager
    )

print("\n✅ Données de démo créées avec succès !")
print("\n📋 Comptes disponibles :")
print("  Manager      → manager@smodu.ma    / Demo1234!")
print("  Apprenant 1  → sara@smodu.ma       / Demo1234!  (TRAINING)")
print("  Apprenant 2  → youssef@smodu.ma    / Demo1234!  (EVALUATION)")
print("  Apprenant 3  → nadia@smodu.ma      / Demo1234!  (ONBOARDING)")
print("  Apprenant 4  → mehdi@smodu.ma      / Demo1234!  (VALIDATED)")

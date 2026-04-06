"""Modèles utilisateurs : CustomUser, rôles et profil."""

import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class Role(models.TextChoices):
    """Rôles disponibles sur la plateforme SMODU."""

    ADMIN = "ADMIN", "Administrateur"
    HR = "HR", "RH"
    MANAGER = "MANAGER", "Manager"
    TRAINER = "TRAINER", "Formateur"
    ODOO_REF = "ODOO_REF", "Référent Odoo"
    LEARNER = "LEARNER", "Apprenant"


class CustomUserManager(BaseUserManager):
    """Manager personnalisé — email comme identifiant unique."""

    def create_user(self, email, password=None, **extra_fields):
        """Crée et retourne un utilisateur standard."""
        if not email:
            raise ValueError("L'adresse email est obligatoire.")
        email = self.normalize_email(email)
        extra_fields.setdefault("role", Role.LEARNER)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Crée et retourne un superutilisateur."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", Role.ADMIN)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Modèle utilisateur principal de SMODU.
    Identifiant : email (pas username).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    first_name = models.CharField(max_length=150, verbose_name="Prénom")
    last_name = models.CharField(max_length=150, verbose_name="Nom")
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.LEARNER,
        verbose_name="Rôle",
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Département / équipe",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True,
        verbose_name="Avatar",
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    is_staff = models.BooleanField(default=False, verbose_name="Staff admin")
    date_joined = models.DateTimeField(
        auto_now_add=True, verbose_name="Date d'inscription"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Dernière modification"
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"

    def get_full_name(self):
        """Retourne le nom complet."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_admin(self):
        return self.role == Role.ADMIN

    @property
    def is_manager(self):
        return self.role in (Role.MANAGER, Role.HR)

    @property
    def is_trainer(self):
        return self.role in (Role.TRAINER, Role.ODOO_REF)

    @property
    def is_learner(self):
        return self.role == Role.LEARNER


class UserProfile(models.Model):
    """
    Informations complémentaires liées au parcours d'un apprenant.
    Relation 1-to-1 avec CustomUser.
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Utilisateur",
    )
    bio = models.TextField(blank=True, verbose_name="Biographie")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    start_date = models.DateField(
        null=True, blank=True, verbose_name="Date de prise de poste"
    )
    contract_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Type de contrat",
        help_text="Ex : CDI, CDD, Stage, Alternance",
    )
    project_status = models.CharField(
        max_length=30,
        default="ONBOARDING",
        verbose_name="Statut projet",
        choices=[
            ("ONBOARDING", "En onboarding"),
            ("TRAINING", "En formation"),
            ("EVALUATION", "En évaluation"),
            ("CONSOLIDATION", "En consolidation"),
            ("VALIDATED", "Validé pour projet"),
            ("NOT_READY", "Non encore prêt"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self):
        return f"Profil de {self.user.get_full_name()}"

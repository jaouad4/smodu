"""Enregistrement des modèles dans l'interface admin Django."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profil"


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = [
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "date_joined",
    ]
    list_filter = ["role", "is_active", "department"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-date_joined"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Informations personnelles",
            {"fields": ("first_name", "last_name", "department", "avatar")},
        ),
        (
            "Rôle & Permissions",
            {
                "fields": (
                    "role",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Dates", {"fields": ("date_joined", "last_login")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "role",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    readonly_fields = ["date_joined", "last_login"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "contract_type", "project_status", "start_date"]
    list_filter = ["project_status", "contract_type"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]

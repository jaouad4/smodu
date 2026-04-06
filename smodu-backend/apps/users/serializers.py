"""Serializers pour les utilisateurs et l'authentification."""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer du profil complémentaire."""

    class Meta:
        model = UserProfile
        fields = [
            "bio",
            "phone",
            "start_date",
            "contract_type",
            "project_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    """Serializer complet d'un utilisateur (lecture)."""

    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "department",
            "avatar",
            "is_active",
            "date_joined",
            "updated_at",
            "profile",
        ]
        read_only_fields = ["id", "date_joined", "updated_at"]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'un utilisateur (admin)."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "role",
            "department",
            "password",
            "password_confirm",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password": "Les mots de passe ne correspondent pas."}
            )
        return attrs

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour du profil (utilisateur connecté)."""

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "department", "avatar"]


class SMODUTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT enrichi avec les infos utilisateur dans le token."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role
        token["full_name"] = user.get_full_name()
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data

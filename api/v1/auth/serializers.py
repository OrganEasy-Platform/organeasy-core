"""Serializers de autenticação JWT (login / refresh / logout)."""

from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.tokens import OrganEasyRefreshToken, build_token_pair_payload

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.auth_failed = False

    def validate(self, attrs: dict) -> dict:
        email = attrs["email"].strip().lower()
        password = attrs["password"]
        request = self.context.get("request")
        user = authenticate(request=request, username=email, password=password)
        if user is None or not user.is_active:
            self.auth_failed = True
            raise serializers.ValidationError(
                {"detail": "Credenciais inválidas."},
            )
        attrs["user"] = user
        attrs["email"] = email
        return attrs

    def create_tokens(self) -> dict:
        return build_token_pair_payload(self.validated_data["user"])


class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    token_type = serializers.CharField(read_only=True)
    expires_in = serializers.IntegerField(read_only=True)


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs: dict) -> dict:
        raw = attrs["refresh"]
        try:
            token = OrganEasyRefreshToken(raw)
        except TokenError as exc:
            raise serializers.ValidationError(
                {"detail": "Refresh token inválido ou expirado."},
            ) from exc
        attrs["token"] = token
        return attrs

    def create_tokens(self) -> dict:
        token: OrganEasyRefreshToken = self.validated_data["token"]
        user_id = token.payload.get("sub") or token.payload.get("user_id")
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist as exc:
            raise TokenError("User not found") from exc
        if not user.is_active:
            raise TokenError("User inactive")
        try:
            token.blacklist()
        except AttributeError:
            pass
        return build_token_pair_payload(user)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self, **kwargs) -> None:
        """Blacklist do refresh; TokenError propaga para a view (401)."""
        token = RefreshToken(self.validated_data["refresh"])
        token.blacklist()

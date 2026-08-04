"""Tokens JWT OrganEasy (claims mínimas — ADR 0003)."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


def _apply_platform_claims(token: AccessToken | RefreshToken) -> None:
    """Claims de plataforma (placeholders até Fases 4–5)."""
    # org_id explícito null (Fase 3); org ativa = Fase 4; RBAC = Fase 5.
    token["org_id"] = None
    token["roles"] = []
    token["scopes"] = []


class OrganEasyAccessToken(AccessToken):
    """Access token com claims de plataforma."""

    @classmethod
    def for_user(cls, user: AbstractBaseUser) -> OrganEasyAccessToken:
        token = super().for_user(user)
        _apply_platform_claims(token)
        return token


class OrganEasyRefreshToken(RefreshToken):
    """Refresh token que emite OrganEasyAccessToken com as mesmas claims de plataforma."""

    access_token_class = OrganEasyAccessToken

    @classmethod
    def for_user(cls, user: AbstractBaseUser) -> OrganEasyRefreshToken:
        token = super().for_user(user)
        _apply_platform_claims(token)
        return token

    @property
    def access_token(self) -> OrganEasyAccessToken:
        access = super().access_token
        _apply_platform_claims(access)
        return access


def build_token_pair_payload(user: AbstractBaseUser) -> dict[str, Any]:
    """Monta o payload de resposta de login/refresh (access + refresh)."""
    refresh = OrganEasyRefreshToken.for_user(user)
    access = refresh.access_token
    return {
        "access": str(access),
        "refresh": str(refresh),
        "token_type": "Bearer",
        "expires_in": int(access.lifetime.total_seconds()),
    }

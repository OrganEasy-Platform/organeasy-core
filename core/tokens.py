"""Tokens JWT OrganEasy (claims mínimas — ADR 0003)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from organizations.models import Organization


def _normalize_org_id(org_id: UUID | str | None) -> str | None:
    if org_id is None or org_id == "":
        return None
    return str(org_id)


def _apply_platform_claims(
    token: AccessToken | RefreshToken,
    *,
    org_id: UUID | str | None = None,
) -> None:
    """Claims de plataforma (org_id Fase 4; roles/scopes vazios até Fase 5)."""
    token["org_id"] = _normalize_org_id(org_id)
    token["roles"] = []
    token["scopes"] = []


class OrganEasyAccessToken(AccessToken):
    """Access token com claims de plataforma."""

    @classmethod
    def for_user(
        cls,
        user: AbstractBaseUser,
        *,
        org_id: UUID | str | None = None,
    ) -> OrganEasyAccessToken:
        token = super().for_user(user)
        _apply_platform_claims(token, org_id=org_id)
        return token


class OrganEasyRefreshToken(RefreshToken):
    """Refresh token que emite OrganEasyAccessToken com as mesmas claims de plataforma."""

    access_token_class = OrganEasyAccessToken

    @classmethod
    def for_user(
        cls,
        user: AbstractBaseUser,
        *,
        org_id: UUID | str | None = None,
    ) -> OrganEasyRefreshToken:
        token = super().for_user(user)
        _apply_platform_claims(token, org_id=org_id)
        return token

    @property
    def access_token(self) -> OrganEasyAccessToken:
        access = super().access_token
        _apply_platform_claims(access, org_id=self.get("org_id"))
        return access


def build_token_pair_payload(
    user: AbstractBaseUser,
    *,
    organization: Organization | None = None,
) -> dict[str, Any]:
    """Monta o payload de resposta de login/refresh/switch (access + refresh)."""
    org_id = organization.id if organization is not None else None
    refresh = OrganEasyRefreshToken.for_user(user, org_id=org_id)
    access = refresh.access_token
    return {
        "access": str(access),
        "refresh": str(refresh),
        "token_type": "Bearer",
        "expires_in": int(access.lifetime.total_seconds()),
    }

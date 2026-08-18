"""Troca de organização ativa (contexto de tenant) — Fase 4."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from rest_framework_simplejwt.tokens import RefreshToken

from core.audit import record_audit
from core.models import AuditLog
from core.tokens import build_token_pair_payload
from organizations.services import assert_user_can_use_organization


def switch_active_organization(
    *,
    user,
    organization_id: UUID | str,
    from_org_id: str | None = None,
    refresh_raw: str | None = None,
) -> dict[str, Any]:
    """
    Valida membership, emite nova pair com org_id alvo e registra auditoria.

    Se `refresh_raw` for enviado, entra na blacklist antes da emissão
    (TokenError propaga para a view → 401).
    """
    organization = assert_user_can_use_organization(
        user=user,
        organization_id=organization_id,
    )

    if refresh_raw:
        RefreshToken(refresh_raw).blacklist()

    tokens = build_token_pair_payload(user, organization=organization)
    record_audit(
        actor=user,
        action=AuditLog.Action.SWITCH_CONTEXT,
        entity_type=AuditLog.EntityType.ORGANIZATION,
        entity_id=organization.id,
        organization=organization,
        changes={
            "from_org_id": from_org_id,
            "to_org_id": str(organization.id),
        },
    )
    return tokens

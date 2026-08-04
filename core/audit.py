"""Helpers de auditoria administrativa (sem senhas/tokens)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from django.db import models

from core.models import AuditLog

SENSITIVE_FIELDS = frozenset(
    {
        "password",
        "password1",
        "password2",
        "token",
        "access",
        "refresh",
        "secret",
    }
)


def sanitize_changes(changes: dict[str, Any]) -> dict[str, Any]:
    """Remove campos sensíveis do diff de auditoria."""
    cleaned: dict[str, Any] = {}
    for key, value in changes.items():
        if key.lower() in SENSITIVE_FIELDS:
            continue
        cleaned[key] = value
    return cleaned


def build_model_diff(
    old: models.Model | None,
    new: models.Model,
    fields: list[str],
) -> dict[str, dict[str, Any]]:
    """Monta diff campo → {old, new} para os campos informados."""
    changes: dict[str, dict[str, Any]] = {}
    for field in fields:
        new_value = getattr(new, field)
        old_value = getattr(old, field) if old is not None else None
        if old is None or old_value != new_value:
            changes[field] = {"old": old_value, "new": new_value}
    return changes


def record_audit(
    *,
    actor,
    action: str,
    entity_type: str,
    entity_id: UUID,
    changes: dict[str, Any] | None = None,
    organization=None,
) -> AuditLog:
    """Persiste um AuditLog sanitizado."""
    return AuditLog.objects.create(
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        organization=organization,
        changes=sanitize_changes(changes or {}),
    )

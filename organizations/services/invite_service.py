"""Códigos de convite de organização (Pacote B)."""

from __future__ import annotations

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from core.audit import record_audit
from core.models import AuditLog
from core.tokens import build_token_pair_payload
from organizations.models import OrganizationInviteCode, generate_invite_code
from organizations.services.exceptions import AlreadyMemberError, InviteCodeInvalidError
from organizations.services.onboarding_service import (
    _activate_or_create_membership,
    _ensure_not_active_member,
)
from organizations.services.tenant_service import assert_user_can_use_organization


def create_invite_code(*, user, organization_id) -> OrganizationInviteCode:
    """Gera código ativo; requer membership active na org."""
    organization = assert_user_can_use_organization(
        user=user,
        organization_id=organization_id,
    )
    for _ in range(8):
        code = generate_invite_code()
        if not OrganizationInviteCode.objects.filter(code=code).exists():
            invite = OrganizationInviteCode.objects.create(
                organization=organization,
                code=code,
                created_by=user,
                is_active=True,
            )
            record_audit(
                actor=user,
                action=AuditLog.Action.CREATE,
                entity_type=AuditLog.EntityType.INVITE_CODE,
                entity_id=invite.id,
                organization=organization,
                changes={"code": code},
            )
            return invite
    raise RuntimeError("Não foi possível gerar código de convite único.")


def list_invite_codes(*, user, organization_id):
    assert_user_can_use_organization(user=user, organization_id=organization_id)
    return OrganizationInviteCode.objects.filter(
        organization_id=organization_id,
    ).order_by("-created_at")


def deactivate_invite_code(*, user, organization_id, invite_id) -> OrganizationInviteCode:
    organization = assert_user_can_use_organization(
        user=user,
        organization_id=organization_id,
    )
    try:
        invite = OrganizationInviteCode.objects.get(
            id=invite_id,
            organization_id=organization_id,
        )
    except OrganizationInviteCode.DoesNotExist as exc:
        raise InviteCodeInvalidError("Código de convite inválido.") from exc
    if not invite.is_active:
        return invite
    invite.is_active = False
    invite.save(update_fields=["is_active", "updated_at"])
    record_audit(
        actor=user,
        action=AuditLog.Action.STATUS_CHANGE,
        entity_type=AuditLog.EntityType.INVITE_CODE,
        entity_id=invite.id,
        organization=organization,
        changes={"is_active": {"old": True, "new": False}},
    )
    return invite


@transaction.atomic
def redeem_invite_code(*, user, code: str) -> dict:
    """
    Resgata código → membership active + tokens com org_id.

    Código inválido/expirado → InviteCodeInvalidError (403, sem enumerar detalhes).
    """
    normalized = (code or "").strip().upper()
    try:
        invite = (
            OrganizationInviteCode.objects.select_related("organization")
            .select_for_update()
            .get(code=normalized)
        )
    except OrganizationInviteCode.DoesNotExist as exc:
        raise InviteCodeInvalidError("Código de convite inválido.") from exc

    if not invite.is_redeemable():
        raise InviteCodeInvalidError("Código de convite inválido.")

    organization = invite.organization
    try:
        _ensure_not_active_member(user=user, organization=organization)
    except AlreadyMemberError:
        raise

    membership = _activate_or_create_membership(
        user=user,
        organization=organization,
        set_default_if_first=True,
    )
    OrganizationInviteCode.objects.filter(pk=invite.pk).update(
        use_count=F("use_count") + 1,
        updated_at=timezone.now(),
    )
    invite.refresh_from_db(fields=["use_count", "updated_at"])

    record_audit(
        actor=user,
        action=AuditLog.Action.REDEEM,
        entity_type=AuditLog.EntityType.INVITE_CODE,
        entity_id=invite.id,
        organization=organization,
        changes={"user_id": str(user.id)},
    )
    record_audit(
        actor=user,
        action=AuditLog.Action.CREATE,
        entity_type=AuditLog.EntityType.MEMBERSHIP,
        entity_id=membership.id,
        organization=organization,
        changes={"via": "invite_code", "user_id": str(user.id)},
    )
    tokens = build_token_pair_payload(user, organization=organization)
    return {
        "organization": organization,
        "membership": membership,
        "tokens": tokens,
        "invite": invite,
    }

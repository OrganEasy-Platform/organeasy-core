"""Pedidos de entrada em organização (Pacote B)."""

from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from core.audit import record_audit
from core.models import AuditLog
from organizations.models import Organization, OrganizationJoinRequest
from organizations.services.exceptions import (
    AlreadyMemberError,
    JoinRequestAlreadyPendingError,
    JoinRequestInvalidStateError,
)
from organizations.services.onboarding_service import (
    _activate_or_create_membership,
    _ensure_not_active_member,
)
from organizations.services.tenant_service import (
    OrganizationNotAllowedError,
    assert_user_can_use_organization,
)


def create_join_request(*, user, organization_id, message: str = "") -> OrganizationJoinRequest:
    try:
        organization = Organization.objects.get(
            pk=organization_id,
            status=Organization.Status.ACTIVE,
        )
    except Organization.DoesNotExist as exc:
        # Anti-enumeração: mesma mensagem que "não permitido".
        raise OrganizationNotAllowedError(
            "Organização não permitida para este usuário."
        ) from exc

    try:
        _ensure_not_active_member(user=user, organization=organization)
    except AlreadyMemberError:
        raise

    if OrganizationJoinRequest.objects.filter(
        user=user,
        organization=organization,
        status=OrganizationJoinRequest.Status.PENDING,
    ).exists():
        raise JoinRequestAlreadyPendingError(
            "Já existe um pedido pendente para esta organização."
        )

    join_request = OrganizationJoinRequest.objects.create(
        organization=organization,
        user=user,
        status=OrganizationJoinRequest.Status.PENDING,
        message=(message or "").strip()[:500],
    )
    record_audit(
        actor=user,
        action=AuditLog.Action.CREATE,
        entity_type=AuditLog.EntityType.JOIN_REQUEST,
        entity_id=join_request.id,
        organization=organization,
        changes={"status": "pending"},
    )
    return join_request


def list_join_requests(*, user, organization_id, status: str | None = None):
    assert_user_can_use_organization(user=user, organization_id=organization_id)
    qs = OrganizationJoinRequest.objects.filter(
        organization_id=organization_id,
    ).select_related("user").order_by("-created_at")
    if status:
        qs = qs.filter(status=status)
    return qs


def cancel_join_request(*, user, request_id) -> OrganizationJoinRequest:
    try:
        join_request = OrganizationJoinRequest.objects.select_related("organization").get(
            pk=request_id,
            user=user,
        )
    except OrganizationJoinRequest.DoesNotExist as exc:
        raise JoinRequestInvalidStateError("Pedido de entrada inválido.") from exc
    if join_request.status != OrganizationJoinRequest.Status.PENDING:
        raise JoinRequestInvalidStateError("Pedido de entrada não está pendente.")
    join_request.status = OrganizationJoinRequest.Status.CANCELLED
    join_request.reviewed_at = timezone.now()
    join_request.save(update_fields=["status", "reviewed_at", "updated_at"])
    record_audit(
        actor=user,
        action=AuditLog.Action.CANCEL,
        entity_type=AuditLog.EntityType.JOIN_REQUEST,
        entity_id=join_request.id,
        organization=join_request.organization,
        changes={"status": {"old": "pending", "new": "cancelled"}},
    )
    return join_request


@transaction.atomic
def approve_join_request(*, reviewer, organization_id, request_id) -> OrganizationJoinRequest:
    organization = assert_user_can_use_organization(
        user=reviewer,
        organization_id=organization_id,
    )
    try:
        join_request = (
            OrganizationJoinRequest.objects.select_for_update()
            .select_related("user")
            .get(pk=request_id, organization_id=organization_id)
        )
    except OrganizationJoinRequest.DoesNotExist as exc:
        raise JoinRequestInvalidStateError("Pedido de entrada inválido.") from exc
    if join_request.status != OrganizationJoinRequest.Status.PENDING:
        raise JoinRequestInvalidStateError("Pedido de entrada não está pendente.")

    membership = _activate_or_create_membership(
        user=join_request.user,
        organization=organization,
        set_default_if_first=True,
    )
    join_request.status = OrganizationJoinRequest.Status.APPROVED
    join_request.reviewed_by = reviewer
    join_request.reviewed_at = timezone.now()
    join_request.save(
        update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"]
    )
    record_audit(
        actor=reviewer,
        action=AuditLog.Action.APPROVE,
        entity_type=AuditLog.EntityType.JOIN_REQUEST,
        entity_id=join_request.id,
        organization=organization,
        changes={
            "status": {"old": "pending", "new": "approved"},
            "user_id": str(join_request.user_id),
            "membership_id": str(membership.id),
        },
    )
    return join_request


@transaction.atomic
def reject_join_request(*, reviewer, organization_id, request_id) -> OrganizationJoinRequest:
    organization = assert_user_can_use_organization(
        user=reviewer,
        organization_id=organization_id,
    )
    try:
        join_request = OrganizationJoinRequest.objects.select_for_update().get(
            pk=request_id,
            organization_id=organization_id,
        )
    except OrganizationJoinRequest.DoesNotExist as exc:
        raise JoinRequestInvalidStateError("Pedido de entrada inválido.") from exc
    if join_request.status != OrganizationJoinRequest.Status.PENDING:
        raise JoinRequestInvalidStateError("Pedido de entrada não está pendente.")

    join_request.status = OrganizationJoinRequest.Status.REJECTED
    join_request.reviewed_by = reviewer
    join_request.reviewed_at = timezone.now()
    join_request.save(
        update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"]
    )
    record_audit(
        actor=reviewer,
        action=AuditLog.Action.REJECT,
        entity_type=AuditLog.EntityType.JOIN_REQUEST,
        entity_id=join_request.id,
        organization=organization,
        changes={"status": {"old": "pending", "new": "rejected"}},
    )
    return join_request

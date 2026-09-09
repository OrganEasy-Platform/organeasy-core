"""Criação de organização e membership (Pacote B)."""

from __future__ import annotations

from django.conf import settings
from django.db import transaction
from django.utils.text import slugify

from core.audit import record_audit
from core.models import AuditLog
from core.tokens import build_token_pair_payload
from organizations.models import Organization, OrganizationMembership
from organizations.services.exceptions import (
    AlreadyMemberError,
    OrgCreateLimitReachedError,
)


def _unique_slug(base: str) -> str:
    base_slug = slugify(base)[:80] or "org"
    slug = base_slug
    suffix = 2
    while Organization.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{suffix}"
        suffix += 1
    return slug


def count_organizations_created_by(*, user) -> int:
    """Conta só orgs com created_by=user (Admin/legado com null não entram)."""
    return Organization.objects.filter(created_by=user).count()


def ensure_can_create_organization(*, user) -> None:
    limit = int(getattr(settings, "ORG_CREATE_LIMIT", 1))
    if count_organizations_created_by(user=user) >= limit:
        raise OrgCreateLimitReachedError(
            "Limite de organizações criadas atingido."
        )


def _ensure_not_active_member(*, user, organization: Organization) -> None:
    if OrganizationMembership.objects.filter(
        user=user,
        organization=organization,
        status=OrganizationMembership.Status.ACTIVE,
    ).exists():
        raise AlreadyMemberError("Usuário já é membro desta organização.")


def _activate_or_create_membership(
    *,
    user,
    organization: Organization,
    set_default_if_first: bool,
) -> OrganizationMembership:
    has_default = OrganizationMembership.objects.filter(
        user=user,
        is_default=True,
    ).exists()
    is_default = set_default_if_first and not has_default

    membership = OrganizationMembership.objects.filter(
        user=user,
        organization=organization,
    ).first()
    if membership is None:
        return OrganizationMembership.objects.create(
            user=user,
            organization=organization,
            status=OrganizationMembership.Status.ACTIVE,
            is_default=is_default,
        )
    membership.status = OrganizationMembership.Status.ACTIVE
    if is_default:
        membership.is_default = True
    membership.save(update_fields=["status", "is_default", "updated_at"])
    return membership


@transaction.atomic
def create_organization(*, user, name: str, slug: str | None = None) -> dict:
    """
    Cria organização + membership active do criador.

    Retorna {organization, membership, tokens}.
    """
    ensure_can_create_organization(user=user)
    final_slug = _unique_slug(slug.strip() if slug else name)
    organization = Organization.objects.create(
        name=name.strip(),
        slug=final_slug,
        status=Organization.Status.ACTIVE,
        created_by=user,
    )
    membership = _activate_or_create_membership(
        user=user,
        organization=organization,
        set_default_if_first=True,
    )
    record_audit(
        actor=user,
        action=AuditLog.Action.CREATE,
        entity_type=AuditLog.EntityType.ORGANIZATION,
        entity_id=organization.id,
        organization=organization,
        changes={"name": name, "slug": final_slug, "created_by": str(user.id)},
    )
    record_audit(
        actor=user,
        action=AuditLog.Action.CREATE,
        entity_type=AuditLog.EntityType.MEMBERSHIP,
        entity_id=membership.id,
        organization=organization,
        changes={"user_id": str(user.id), "status": membership.status},
    )
    tokens = build_token_pair_payload(user, organization=organization)
    return {
        "organization": organization,
        "membership": membership,
        "tokens": tokens,
    }

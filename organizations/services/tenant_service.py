"""Contexto de tenant (organização ativa) — Fase 4."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from organizations.models import Organization, OrganizationMembership
from organizations.services.organization_service import list_available_organizations

ResolveSource = Literal["explicit", "default", "single", "none"]


class OrganizationNotAllowedError(Exception):
    """Usuário não pode usar a organização informada como contexto ativo."""


class OrganizationContextRequiredError(Exception):
    """Operação exige organização ativa no contexto (org_id no token)."""


class OrganizationMembershipLostError(Exception):
    """org_id do token não corresponde mais a membership ativo."""


def assert_user_can_use_organization(*, user, organization_id: UUID | str) -> Organization:
    """
    Valida membership active + org active.

    Nunca distingue "org inexistente" de "sem vínculo" (anti-enumeração → 403).
    """
    try:
        membership = (
            OrganizationMembership.objects.select_related("organization")
            .get(
                user=user,
                organization_id=organization_id,
                status=OrganizationMembership.Status.ACTIVE,
                organization__status=Organization.Status.ACTIVE,
            )
        )
    except OrganizationMembership.DoesNotExist as exc:
        raise OrganizationNotAllowedError(
            "Organização não permitida para este usuário."
        ) from exc
    return membership.organization


def resolve_active_organization(
    *,
    user,
    organization_id: UUID | str | None = None,
) -> tuple[Organization | None, ResolveSource]:
    """
    Resolve org ativa: explicit → default → única disponível → none.

    Se `organization_id` for informado e inválido, levanta OrganizationNotAllowedError.
    """
    if organization_id is not None:
        return assert_user_can_use_organization(
            user=user,
            organization_id=organization_id,
        ), "explicit"

    default_membership = (
        OrganizationMembership.objects.select_related("organization")
        .filter(
            user=user,
            is_default=True,
            status=OrganizationMembership.Status.ACTIVE,
            organization__status=Organization.Status.ACTIVE,
        )
        .first()
    )
    if default_membership is not None:
        return default_membership.organization, "default"

    available = list(list_available_organizations(user=user)[:2])
    if len(available) == 1:
        return available[0], "single"
    return None, "none"


def require_organization_context(*, org_id: UUID | str | None) -> str:
    """Garante org_id presente; retorna string normalizada do UUID."""
    if org_id is None or org_id == "":
        raise OrganizationContextRequiredError(
            "Contexto de organização é obrigatório para esta operação."
        )
    return str(org_id)


def revalidate_organization_from_claim(*, user, org_id: UUID | str | None) -> Organization | None:
    """
    Revalida org_id do refresh/access.

    - None → None (login sem org ainda permitido no Pacote A).
    - Preenchido e inválido → OrganizationMembershipLostError (403 no refresh).
    """
    if org_id is None or org_id == "":
        return None
    try:
        return assert_user_can_use_organization(user=user, organization_id=org_id)
    except OrganizationNotAllowedError as exc:
        raise OrganizationMembershipLostError(
            "Vínculo com a organização ativa não é mais válido."
        ) from exc

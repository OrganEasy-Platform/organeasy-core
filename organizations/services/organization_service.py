"""Service de listagem de organizações do usuário autenticado."""

from __future__ import annotations

from django.db.models import QuerySet

from organizations.models import Organization, OrganizationMembership


def list_available_organizations(*, user) -> QuerySet[Organization]:
    """
    Retorna organizações ativas com membership ativo do usuário.

    Fonte de verdade: vínculo OrganizationMembership (nunca organization_id do client).
    """
    return (
        Organization.objects.filter(
            status=Organization.Status.ACTIVE,
            memberships__user=user,
            memberships__status=OrganizationMembership.Status.ACTIVE,
        )
        .distinct()
        .order_by("name")
    )


def get_membership_flags(*, user, organizations: list[Organization]) -> dict:
    """Mapa organization_id → (is_default, membership_status) para serialização."""
    org_ids = [org.id for org in organizations]
    memberships = OrganizationMembership.objects.filter(
        user=user,
        organization_id__in=org_ids,
        status=OrganizationMembership.Status.ACTIVE,
    ).only("organization_id", "is_default", "status")
    return {
        m.organization_id: {
            "is_default": m.is_default,
            "membership_status": m.status,
        }
        for m in memberships
    }

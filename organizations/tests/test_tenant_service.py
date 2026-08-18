"""Testes do contexto de tenant (Fase 4)."""

from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from organizations.models import Organization, OrganizationMembership
from organizations.services import (
    OrganizationContextRequiredError,
    OrganizationMembershipLostError,
    OrganizationNotAllowedError,
    assert_user_can_use_organization,
    require_organization_context,
    resolve_active_organization,
    revalidate_organization_from_claim,
)

User = get_user_model()


class TenantServiceTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="tenant@example.com",
            password="secure-pass-123",
            full_name="Tenant User",
        )
        self.org_a = Organization.objects.create(name="Acme", slug="acme")
        self.org_b = Organization.objects.create(name="Beta", slug="beta")
        self.org_inactive = Organization.objects.create(
            name="Off",
            slug="off",
            status=Organization.Status.INACTIVE,
        )

    def test_resolve_explicit(self) -> None:
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_a,
            is_default=True,
        )
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_b,
        )
        org, source = resolve_active_organization(
            user=self.user,
            organization_id=self.org_b.id,
        )
        self.assertEqual(org, self.org_b)
        self.assertEqual(source, "explicit")

    def test_resolve_default(self) -> None:
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_a,
            is_default=True,
        )
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_b,
        )
        org, source = resolve_active_organization(user=self.user)
        self.assertEqual(org, self.org_a)
        self.assertEqual(source, "default")

    def test_resolve_single(self) -> None:
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_a,
        )
        org, source = resolve_active_organization(user=self.user)
        self.assertEqual(org, self.org_a)
        self.assertEqual(source, "single")

    def test_resolve_none_when_zero_or_many_without_default(self) -> None:
        org, source = resolve_active_organization(user=self.user)
        self.assertIsNone(org)
        self.assertEqual(source, "none")

        OrganizationMembership.objects.create(user=self.user, organization=self.org_a)
        OrganizationMembership.objects.create(user=self.user, organization=self.org_b)
        org, source = resolve_active_organization(user=self.user)
        self.assertIsNone(org)
        self.assertEqual(source, "none")

    def test_explicit_invalid_raises_not_allowed(self) -> None:
        with self.assertRaises(OrganizationNotAllowedError):
            resolve_active_organization(
                user=self.user,
                organization_id=uuid.uuid4(),
            )
        with self.assertRaises(OrganizationNotAllowedError):
            assert_user_can_use_organization(
                user=self.user,
                organization_id=self.org_a.id,
            )

    def test_require_context(self) -> None:
        self.assertEqual(require_organization_context(org_id=self.org_a.id), str(self.org_a.id))
        with self.assertRaises(OrganizationContextRequiredError):
            require_organization_context(org_id=None)

    def test_revalidate_lost_membership(self) -> None:
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_a,
            status=OrganizationMembership.Status.INACTIVE,
        )
        with self.assertRaises(OrganizationMembershipLostError):
            revalidate_organization_from_claim(user=self.user, org_id=self.org_a.id)
        self.assertIsNone(revalidate_organization_from_claim(user=self.user, org_id=None))

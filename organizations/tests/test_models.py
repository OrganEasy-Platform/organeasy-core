"""Testes de Organization e Membership."""

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from organizations.models import Organization, OrganizationMembership

User = get_user_model()


class OrganizationModelTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="member@example.com",
            password="secure-pass-123",
            full_name="Member",
        )
        self.org_a = Organization.objects.create(name="Org A", slug="org-a")
        self.org_b = Organization.objects.create(name="Org B", slug="org-b")

    def test_unique_user_organization_membership(self) -> None:
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_a,
        )
        with self.assertRaises(IntegrityError):
            OrganizationMembership.objects.create(
                user=self.user,
                organization=self.org_a,
            )

    def test_only_one_default_membership_per_user(self) -> None:
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_a,
            is_default=True,
        )
        with self.assertRaises(IntegrityError):
            OrganizationMembership.objects.create(
                user=self.user,
                organization=self.org_b,
                is_default=True,
            )

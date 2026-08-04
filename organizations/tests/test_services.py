"""Testes do service de organizações disponíveis."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from organizations.models import Organization, OrganizationMembership
from organizations.services import list_available_organizations

User = get_user_model()


class OrganizationServiceTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="u@example.com",
            password="secure-pass-123",
            full_name="User",
        )
        self.other = User.objects.create_user(
            email="other@example.com",
            password="secure-pass-123",
            full_name="Other",
        )
        self.org_a = Organization.objects.create(name="A", slug="a")
        self.org_b = Organization.objects.create(name="B", slug="b")
        self.org_c = Organization.objects.create(
            name="C",
            slug="c",
            status=Organization.Status.INACTIVE,
        )

    def test_lists_only_active_memberships_and_orgs(self) -> None:
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_a,
            is_default=True,
        )
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_b,
            status=OrganizationMembership.Status.INACTIVE,
        )
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_c,
        )
        OrganizationMembership.objects.create(
            user=self.other,
            organization=self.org_b,
        )

        qs = list_available_organizations(user=self.user)
        self.assertEqual(list(qs), [self.org_a])

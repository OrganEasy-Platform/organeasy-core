"""Testes dos endpoints /api/v1/me/."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from organizations.models import Organization, OrganizationMembership

User = get_user_model()


class MeApiTests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="me@example.com",
            password="secure-pass-123",
            full_name="Me User",
        )
        self.org_a = Organization.objects.create(name="Alpha", slug="alpha")
        self.org_b = Organization.objects.create(name="Beta", slug="beta")
        self.org_other = Organization.objects.create(name="Gamma", slug="gamma")
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

    def test_me_requires_authentication(self) -> None:
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.json()["success"])

    def test_me_returns_profile(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertTrue(body["success"])
        self.assertEqual(body["data"]["email"], "me@example.com")
        self.assertEqual(body["data"]["full_name"], "Me User")
        self.assertEqual(body["data"]["status"], "active")
        self.assertIsNone(body["data"]["active_organization"])
        self.assertNotIn("password", body["data"])

    def test_my_organizations_only_active_memberships(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("my-organizations"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertTrue(body["success"])
        slugs = [item["slug"] for item in body["data"]]
        self.assertEqual(slugs, ["alpha"])
        self.assertTrue(body["data"][0]["is_default"])
        self.assertEqual(body["data"][0]["membership_status"], "active")

    def test_my_organizations_excludes_other_users_orgs(self) -> None:
        stranger = User.objects.create_user(
            email="stranger@example.com",
            password="secure-pass-123",
            full_name="Stranger",
        )
        OrganizationMembership.objects.create(
            user=stranger,
            organization=self.org_other,
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("my-organizations"))
        slugs = [item["slug"] for item in response.json()["data"]]
        self.assertNotIn("gamma", slugs)

    def test_blocked_user_cannot_authenticate(self) -> None:
        self.user.status = User.Status.BLOCKED
        self.user.save()
        self.assertFalse(self.user.is_active)
        logged_in = self.client.login(
            email="me@example.com",
            password="secure-pass-123",
        )
        self.assertFalse(logged_in)

"""Testes de autenticação JWT — contexto de tenant (Fase 4)."""

from __future__ import annotations

import uuid

import jwt
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.settings import api_settings

from core.models import AuditLog
from core.tokens import build_token_pair_payload
from organizations.models import Organization, OrganizationMembership

User = get_user_model()


class AuthTenantApiTests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="tenant-api@example.com",
            password="secure-pass-123",
            full_name="Tenant API",
        )
        self.org_a = Organization.objects.create(name="Acme", slug="acme-api")
        self.org_b = Organization.objects.create(name="Beta", slug="beta-api")
        self.login_url = reverse("auth-login")
        self.refresh_url = reverse("auth-refresh")
        self.switch_url = reverse("auth-switch-organization")
        self.me_url = reverse("me")

    def _decode(self, access: str) -> dict:
        return jwt.decode(
            access,
            api_settings.SIGNING_KEY,
            algorithms=[api_settings.ALGORITHM],
            audience=api_settings.AUDIENCE,
            issuer=api_settings.ISSUER,
        )

    def test_login_without_orgs_emits_null_org_id(self) -> None:
        response = self.client.post(
            self.login_url,
            {"email": "tenant-api@example.com", "password": "secure-pass-123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        claims = self._decode(response.json()["data"]["access"])
        self.assertIsNone(claims["org_id"])

    def test_login_uses_default_membership(self) -> None:
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_a,
            is_default=True,
        )
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_b,
        )
        response = self.client.post(
            self.login_url,
            {"email": "tenant-api@example.com", "password": "secure-pass-123"},
            format="json",
        )
        claims = self._decode(response.json()["data"]["access"])
        self.assertEqual(claims["org_id"], str(self.org_a.id))

    def test_login_explicit_organization_id(self) -> None:
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_a,
            is_default=True,
        )
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_b,
        )
        response = self.client.post(
            self.login_url,
            {
                "email": "tenant-api@example.com",
                "password": "secure-pass-123",
                "organization_id": str(self.org_b.id),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        claims = self._decode(response.json()["data"]["access"])
        self.assertEqual(claims["org_id"], str(self.org_b.id))

    def test_login_invalid_organization_returns_403(self) -> None:
        response = self.client.post(
            self.login_url,
            {
                "email": "tenant-api@example.com",
                "password": "secure-pass-123",
                "organization_id": str(uuid.uuid4()),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error_code"], "ORGANIZATION_NOT_ALLOWED")

    def test_switch_organization_emits_new_pair_and_audit(self) -> None:
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_a,
            is_default=True,
        )
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_b,
        )
        login = self.client.post(
            self.login_url,
            {"email": "tenant-api@example.com", "password": "secure-pass-123"},
            format="json",
        )
        pair = login.json()["data"]
        switch = self.client.post(
            self.switch_url,
            {
                "organization_id": str(self.org_b.id),
                "refresh": pair["refresh"],
            },
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {pair['access']}",
        )
        self.assertEqual(switch.status_code, status.HTTP_200_OK)
        claims = self._decode(switch.json()["data"]["access"])
        self.assertEqual(claims["org_id"], str(self.org_b.id))
        self.assertTrue(
            AuditLog.objects.filter(
                action=AuditLog.Action.SWITCH_CONTEXT,
                entity_id=self.org_b.id,
                actor=self.user,
            ).exists()
        )
        reuse = self.client.post(
            self.refresh_url,
            {"refresh": pair["refresh"]},
            format="json",
        )
        self.assertEqual(reuse.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_switch_foreign_org_returns_403(self) -> None:
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_a,
        )
        pair = build_token_pair_payload(self.user, organization=self.org_a)
        response = self.client.post(
            self.switch_url,
            {"organization_id": str(self.org_b.id)},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {pair['access']}",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error_code"], "ORGANIZATION_NOT_ALLOWED")

    def test_refresh_preserves_org_id(self) -> None:
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_a,
        )
        pair = build_token_pair_payload(self.user, organization=self.org_a)
        response = self.client.post(
            self.refresh_url,
            {"refresh": pair["refresh"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        claims = self._decode(response.json()["data"]["access"])
        self.assertEqual(claims["org_id"], str(self.org_a.id))

    def test_refresh_membership_lost_returns_403(self) -> None:
        membership = OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_a,
        )
        pair = build_token_pair_payload(self.user, organization=self.org_a)
        membership.status = OrganizationMembership.Status.INACTIVE
        membership.save(update_fields=["status"])
        response = self.client.post(
            self.refresh_url,
            {"refresh": pair["refresh"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error_code"], "ORGANIZATION_MEMBERSHIP_LOST")

    def test_me_includes_active_organization(self) -> None:
        OrganizationMembership.objects.create(
            user=self.user,
            organization=self.org_a,
            is_default=True,
        )
        pair = build_token_pair_payload(self.user, organization=self.org_a)
        response = self.client.get(
            self.me_url,
            HTTP_AUTHORIZATION=f"Bearer {pair['access']}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        active = response.json()["data"]["active_organization"]
        self.assertEqual(active["id"], str(self.org_a.id))
        self.assertEqual(active["slug"], "acme-api")

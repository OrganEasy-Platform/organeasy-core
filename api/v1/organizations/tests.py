"""Testes da API de onboarding de organizações (Pacote B)."""

from __future__ import annotations

import jwt
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.settings import api_settings

from organizations.models import (
    Organization,
    OrganizationInviteCode,
    OrganizationMembership,
)

User = get_user_model()


class OrganizationOnboardingApiTests(APITestCase):
    def setUp(self) -> None:
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="secure-pass-123",
            full_name="Owner",
        )
        self.member = User.objects.create_user(
            email="member@example.com",
            password="secure-pass-123",
            full_name="Member",
        )
        self.outsider = User.objects.create_user(
            email="out@example.com",
            password="secure-pass-123",
            full_name="Outsider",
        )
        self.create_url = reverse("organization-create")
        self.join_code_url = reverse("organization-join-by-code")

    def _auth(self, user) -> None:
        self.client.force_authenticate(user=user)

    def _decode(self, access: str) -> dict:
        return jwt.decode(
            access,
            api_settings.SIGNING_KEY,
            algorithms=[api_settings.ALGORITHM],
            audience=api_settings.AUDIENCE,
            issuer=api_settings.ISSUER,
        )

    def test_create_organization_returns_tokens_and_sets_default(self) -> None:
        self._auth(self.owner)
        response = self.client.post(
            self.create_url,
            {"name": "Acme Corp"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        body = response.json()
        self.assertTrue(body["success"])
        org_id = body["data"]["organization"]["id"]
        claims = self._decode(body["data"]["tokens"]["access"])
        self.assertEqual(claims["org_id"], org_id)
        org = Organization.objects.get(pk=org_id)
        self.assertEqual(org.created_by_id, self.owner.id)
        membership = OrganizationMembership.objects.get(
            user=self.owner,
            organization=org,
        )
        self.assertTrue(membership.is_default)
        self.assertEqual(membership.status, OrganizationMembership.Status.ACTIVE)

    def test_create_organization_limit_reached(self) -> None:
        self._auth(self.owner)
        first = self.client.post(self.create_url, {"name": "One"}, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        second = self.client.post(self.create_url, {"name": "Two"}, format="json")
        self.assertEqual(second.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(second.json()["error_code"], "ORG_CREATE_LIMIT_REACHED")

    def test_admin_org_without_created_by_does_not_count(self) -> None:
        Organization.objects.create(name="Legacy", slug="legacy", created_by=None)
        self._auth(self.owner)
        response = self.client.post(self.create_url, {"name": "Mine"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invite_code_flow(self) -> None:
        self._auth(self.owner)
        created = self.client.post(self.create_url, {"name": "Invite Org"}, format="json")
        org_id = created.json()["data"]["organization"]["id"]
        access = created.json()["data"]["tokens"]["access"]

        invite_url = reverse("organization-invite-codes", kwargs={"organization_id": org_id})
        invite = self.client.post(
            invite_url,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(invite.status_code, status.HTTP_201_CREATED)
        code = invite.json()["data"]["code"]

        self._auth(self.outsider)
        join = self.client.post(self.join_code_url, {"code": code}, format="json")
        self.assertEqual(join.status_code, status.HTTP_200_OK)
        claims = self._decode(join.json()["data"]["tokens"]["access"])
        self.assertEqual(claims["org_id"], org_id)
        self.assertTrue(
            OrganizationMembership.objects.filter(
                user=self.outsider,
                organization_id=org_id,
                status=OrganizationMembership.Status.ACTIVE,
            ).exists()
        )

    def test_invalid_invite_code_returns_403(self) -> None:
        self._auth(self.outsider)
        response = self.client.post(
            self.join_code_url,
            {"code": "INVALID1"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error_code"], "INVITE_CODE_INVALID")

    def test_join_request_approve_flow(self) -> None:
        self._auth(self.owner)
        created = self.client.post(self.create_url, {"name": "Req Org"}, format="json")
        org_id = created.json()["data"]["organization"]["id"]

        self._auth(self.outsider)
        req_url = reverse(
            "organization-join-requests",
            kwargs={"organization_id": org_id},
        )
        pending = self.client.post(
            req_url,
            {"message": "Quero entrar"},
            format="json",
        )
        self.assertEqual(pending.status_code, status.HTTP_201_CREATED)
        request_id = pending.json()["data"]["id"]

        approve_url = reverse(
            "organization-join-request-approve",
            kwargs={"organization_id": org_id, "request_id": request_id},
        )
        self._auth(self.owner)
        approve = self.client.post(approve_url, format="json")
        self.assertEqual(approve.status_code, status.HTTP_200_OK)
        self.assertEqual(approve.json()["data"]["status"], "approved")
        self.assertTrue(
            OrganizationMembership.objects.filter(
                user=self.outsider,
                organization_id=org_id,
                status=OrganizationMembership.Status.ACTIVE,
            ).exists()
        )

    def test_duplicate_pending_join_request_conflict(self) -> None:
        org = Organization.objects.create(name="Dup", slug="dup", created_by=self.owner)
        OrganizationMembership.objects.create(
            user=self.owner,
            organization=org,
            is_default=True,
        )
        self._auth(self.outsider)
        url = reverse("organization-join-requests", kwargs={"organization_id": org.id})
        first = self.client.post(url, {}, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        second = self.client.post(url, {}, format="json")
        self.assertEqual(second.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(second.json()["error_code"], "JOIN_REQUEST_ALREADY_PENDING")

    def test_cancel_own_join_request(self) -> None:
        org = Organization.objects.create(name="Cancel", slug="cancel", created_by=self.owner)
        self._auth(self.outsider)
        create_url = reverse(
            "organization-join-requests",
            kwargs={"organization_id": org.id},
        )
        pending = self.client.post(create_url, {}, format="json")
        request_id = pending.json()["data"]["id"]
        cancel_url = reverse(
            "organization-join-request-cancel",
            kwargs={"request_id": request_id},
        )
        cancelled = self.client.post(cancel_url, format="json")
        self.assertEqual(cancelled.status_code, status.HTTP_200_OK)
        self.assertEqual(cancelled.json()["data"]["status"], "cancelled")

    def test_already_member_cannot_join_by_code(self) -> None:
        self._auth(self.owner)
        created = self.client.post(self.create_url, {"name": "Same"}, format="json")
        org_id = created.json()["data"]["organization"]["id"]
        access = created.json()["data"]["tokens"]["access"]
        invite_url = reverse("organization-invite-codes", kwargs={"organization_id": org_id})
        code = self.client.post(
            invite_url,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access}",
        ).json()["data"]["code"]
        again = self.client.post(
            self.join_code_url,
            {"code": code},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(again.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(again.json()["error_code"], "ALREADY_MEMBER")

    def test_deactivate_invite_code(self) -> None:
        self._auth(self.owner)
        created = self.client.post(self.create_url, {"name": "Deact"}, format="json")
        org_id = created.json()["data"]["organization"]["id"]
        access = created.json()["data"]["tokens"]["access"]
        invite_url = reverse("organization-invite-codes", kwargs={"organization_id": org_id})
        invite = self.client.post(
            invite_url,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        invite_id = invite.json()["data"]["id"]
        deactivate_url = reverse(
            "organization-invite-code-deactivate",
            kwargs={"organization_id": org_id, "invite_id": invite_id},
        )
        deactivated = self.client.post(
            deactivate_url,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(deactivated.status_code, status.HTTP_200_OK)
        self.assertFalse(deactivated.json()["data"]["is_active"])
        self.assertFalse(
            OrganizationInviteCode.objects.get(pk=invite_id).is_active
        )

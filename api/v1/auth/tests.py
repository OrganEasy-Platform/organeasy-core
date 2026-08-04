"""Testes de autenticação JWT (login / refresh / logout / claims)."""

from __future__ import annotations

from datetime import timedelta

import jwt
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from core.tokens import OrganEasyAccessToken, build_token_pair_payload

User = get_user_model()


class AuthJwtApiTests(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="jwt@example.com",
            password="secure-pass-123",
            full_name="JWT User",
        )
        self.login_url = reverse("auth-login")
        self.refresh_url = reverse("auth-refresh")
        self.logout_url = reverse("auth-logout")
        self.me_url = reverse("me")

    def test_login_returns_token_pair_and_me_with_bearer(self) -> None:
        response = self.client.post(
            self.login_url,
            {"email": "jwt@example.com", "password": "secure-pass-123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        self.assertTrue(body["success"])
        data = body["data"]
        self.assertEqual(data["token_type"], "Bearer")
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertEqual(data["expires_in"], int(api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()))

        me = self.client.get(
            self.me_url,
            HTTP_AUTHORIZATION=f"Bearer {data['access']}",
        )
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.json()["data"]["email"], "jwt@example.com")

    def test_login_invalid_credentials_returns_401(self) -> None:
        response = self.client.post(
            self.login_url,
            {"email": "jwt@example.com", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.json()["success"])
        self.assertEqual(response.json()["error_code"], "AUTHENTICATION_REQUIRED")

    def test_login_blocked_user_returns_401(self) -> None:
        self.user.status = User.Status.BLOCKED
        self.user.save()
        response = self.client.post(
            self.login_url,
            {"email": "jwt@example.com", "password": "secure-pass-123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_claims_match_adr(self) -> None:
        payload = build_token_pair_payload(self.user)
        access = jwt.decode(
            payload["access"],
            api_settings.SIGNING_KEY,
            algorithms=[api_settings.ALGORITHM],
            audience=api_settings.AUDIENCE,
            issuer=api_settings.ISSUER,
        )
        self.assertEqual(access["sub"], str(self.user.id))
        self.assertIsNone(access["org_id"])
        self.assertEqual(access["roles"], [])
        self.assertEqual(access["scopes"], [])
        self.assertEqual(access["iss"], api_settings.ISSUER)
        self.assertEqual(access["aud"], api_settings.AUDIENCE)
        self.assertIn("jti", access)
        self.assertIn("exp", access)
        self.assertIn("iat", access)

    def test_expired_access_rejected_on_me(self) -> None:
        token = OrganEasyAccessToken.for_user(self.user)
        token.set_exp(from_time=timezone.now() - timedelta(hours=1), lifetime=timedelta(seconds=1))
        response = self.client.get(
            self.me_url,
            HTTP_AUTHORIZATION=f"Bearer {str(token)}",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_access_rejected_on_me(self) -> None:
        response = self.client.get(
            self.me_url,
            HTTP_AUTHORIZATION="Bearer not-a-valid-token",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wrong_audience_rejected(self) -> None:
        token = OrganEasyAccessToken.for_user(self.user)
        # Reassina com audience diferente (PyJWT / SimpleJWT validam aud).
        payload = dict(token.payload)
        payload["aud"] = "wrong-audience"
        forged = jwt.encode(
            payload,
            api_settings.SIGNING_KEY,
            algorithm=api_settings.ALGORITHM,
        )
        response = self.client.get(
            self.me_url,
            HTTP_AUTHORIZATION=f"Bearer {forged}",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_rotates_and_blacklists_old(self) -> None:
        pair = build_token_pair_payload(self.user)
        old_refresh = pair["refresh"]
        response = self.client.post(
            self.refresh_url,
            {"refresh": old_refresh},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_data = response.json()["data"]
        self.assertNotEqual(new_data["refresh"], old_refresh)

        reuse = self.client.post(
            self.refresh_url,
            {"refresh": old_refresh},
            format="json",
        )
        self.assertEqual(reuse.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blacklists_refresh(self) -> None:
        pair = build_token_pair_payload(self.user)
        logout = self.client.post(
            self.logout_url,
            {"refresh": pair["refresh"]},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {pair['access']}",
        )
        self.assertEqual(logout.status_code, status.HTTP_200_OK)
        self.assertTrue(logout.json()["success"])
        self.assertIn("Logout", logout.json()["message"])

        refresh = self.client.post(
            self.refresh_url,
            {"refresh": pair["refresh"]},
            format="json",
        )
        self.assertEqual(refresh.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(BlacklistedToken.objects.exists())

    def test_logout_requires_authentication(self) -> None:
        pair = build_token_pair_payload(self.user)
        response = self.client.post(
            self.logout_url,
            {"refresh": pair["refresh"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logs_do_not_contain_full_token(self) -> None:
        with self.assertLogs("api.v1.auth.views", level="INFO") as captured:
            response = self.client.post(
                self.login_url,
                {"email": "jwt@example.com", "password": "secure-pass-123"},
                format="json",
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access = response.json()["data"]["access"]
        joined = "\n".join(captured.output)
        self.assertNotIn(access, joined)
        self.assertIn("login_success", joined)

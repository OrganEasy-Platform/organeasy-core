"""Testes de model User."""

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user_with_email(self) -> None:
        user = User.objects.create_user(
            email="alice@example.com",
            password="secure-pass-123",
            full_name="Alice",
        )
        self.assertEqual(user.email, "alice@example.com")
        self.assertEqual(user.status, User.Status.ACTIVE)
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password("secure-pass-123"))

    def test_blocked_user_sets_is_active_false(self) -> None:
        user = User.objects.create_user(
            email="bob@example.com",
            password="secure-pass-123",
            full_name="Bob",
        )
        user.status = User.Status.BLOCKED
        user.save()
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_email_is_normalized(self) -> None:
        user = User.objects.create_user(
            email="Carol@Example.COM",
            password="secure-pass-123",
            full_name="Carol",
        )
        self.assertEqual(user.email, "Carol@example.com")

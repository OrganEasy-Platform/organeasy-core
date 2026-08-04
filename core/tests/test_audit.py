"""Testes de auditoria administrativa."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.audit import record_audit, sanitize_changes
from core.models import AuditLog
from organizations.models import Organization

User = get_user_model()


class AuditLogTests(TestCase):
    def setUp(self) -> None:
        self.actor = User.objects.create_user(
            email="admin@example.com",
            password="secure-pass-123",
            full_name="Admin",
            is_staff=True,
        )
        self.org = Organization.objects.create(name="Audited", slug="audited")

    def test_sanitize_removes_password(self) -> None:
        cleaned = sanitize_changes(
            {
                "email": {"old": "a@x.com", "new": "b@x.com"},
                "password": {"old": "x", "new": "y"},
            }
        )
        self.assertIn("email", cleaned)
        self.assertNotIn("password", cleaned)

    def test_record_audit_persists_without_sensitive_fields(self) -> None:
        log = record_audit(
            actor=self.actor,
            action=AuditLog.Action.STATUS_CHANGE,
            entity_type=AuditLog.EntityType.ORGANIZATION,
            entity_id=self.org.id,
            organization=self.org,
            changes={
                "status": {"old": "active", "new": "inactive"},
                "password": {"old": "secret", "new": "other"},
            },
        )
        self.assertEqual(log.action, AuditLog.Action.STATUS_CHANGE)
        self.assertEqual(log.changes["status"]["new"], "inactive")
        self.assertNotIn("password", log.changes)

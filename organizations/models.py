"""Models de organização e vínculo usuário-organização."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class Organization(models.Model):
    """Organização (tenant) do OrganEasy."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Ativa"
        INACTIVE = "inactive", "Inativa"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("nome", max_length=255)
    slug = models.SlugField("slug", max_length=100, unique=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "organização"
        verbose_name_plural = "organizações"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class OrganizationMembership(models.Model):
    """Vínculo usuário ↔ organização (fonte do escopo multi-tenant)."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Ativo"
        INACTIVE = "inactive", "Inativo"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name="organização",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name="usuário",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    is_default = models.BooleanField(
        "organização padrão",
        default=False,
        help_text="Preparação para contexto de tenant (Fase 4).",
    )
    joined_at = models.DateTimeField("entrou em", default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "vínculo usuário-organização"
        verbose_name_plural = "vínculos usuário-organização"
        ordering = ["-is_default", "joined_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                name="uniq_user_organization_membership",
            ),
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(is_default=True),
                name="uniq_default_membership_per_user",
            ),
        ]
        indexes = [
            models.Index(
                fields=["user", "status"],
                name="org_memb_user_status_idx",
            ),
            models.Index(
                fields=["organization", "status"],
                name="org_memb_org_status_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} @ {self.organization_id}"

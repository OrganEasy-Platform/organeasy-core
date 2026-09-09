"""Models de organização, vínculo, convite e pedido de entrada."""

from __future__ import annotations

import secrets
import string
import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


def generate_invite_code(length: int = 8) -> str:
    """Gera código alfanumérico uppercase (A-Z0-9)."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


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
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_organizations",
        verbose_name="criada por",
        help_text="Quem criou via API; null = Admin/legado (não conta no limite).",
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
        help_text="Preferência de organização ativa no login (Fase 4).",
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


class OrganizationInviteCode(models.Model):
    """Código de convite para entrar em uma organização."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="invite_codes",
        verbose_name="organização",
    )
    code = models.CharField("código", max_length=32, unique=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_invite_codes",
        verbose_name="criado por",
    )
    is_active = models.BooleanField("ativo", default=True, db_index=True)
    expires_at = models.DateTimeField("expira em", null=True, blank=True)
    max_uses = models.PositiveIntegerField(
        "máximo de usos",
        null=True,
        blank=True,
        help_text="null = ilimitado",
    )
    use_count = models.PositiveIntegerField("usos", default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "código de convite"
        verbose_name_plural = "códigos de convite"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["organization", "is_active"],
                name="org_invite_org_active_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} @ {self.organization_id}"

    def is_redeemable(self) -> bool:
        if not self.is_active:
            return False
        if self.organization.status != Organization.Status.ACTIVE:
            return False
        if self.expires_at is not None and self.expires_at <= timezone.now():
            return False
        if self.max_uses is not None and self.use_count >= self.max_uses:
            return False
        return True


class OrganizationJoinRequest(models.Model):
    """Pedido de entrada em organização (aprovação por membro)."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        APPROVED = "approved", "Aprovado"
        REJECTED = "rejected", "Rejeitado"
        CANCELLED = "cancelled", "Cancelado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="join_requests",
        verbose_name="organização",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="join_requests",
        verbose_name="solicitante",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    message = models.CharField("mensagem", max_length=500, blank=True, default="")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_join_requests",
        verbose_name="revisado por",
    )
    reviewed_at = models.DateTimeField("revisado em", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "pedido de entrada"
        verbose_name_plural = "pedidos de entrada"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                condition=Q(status="pending"),
                name="uniq_pending_join_request_per_user_org",
            ),
        ]
        indexes = [
            models.Index(
                fields=["organization", "status"],
                name="org_join_req_org_status_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} → {self.organization_id} ({self.status})"

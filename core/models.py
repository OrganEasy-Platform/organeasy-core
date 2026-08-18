"""Models compartilhados (auditoria administrativa)."""

from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    """Registro de alterações administrativas sensíveis."""

    class Action(models.TextChoices):
        CREATE = "create", "Criação"
        UPDATE = "update", "Atualização"
        STATUS_CHANGE = "status_change", "Mudança de status"
        SWITCH_CONTEXT = "switch_context", "Troca de contexto"
        REDEEM = "redeem", "Resgate"
        APPROVE = "approve", "Aprovação"
        REJECT = "reject", "Rejeição"
        CANCEL = "cancel", "Cancelamento"

    class EntityType(models.TextChoices):
        USER = "user", "Usuário"
        ORGANIZATION = "organization", "Organização"
        MEMBERSHIP = "membership", "Vínculo"
        INVITE_CODE = "invite_code", "Código de convite"
        JOIN_REQUEST = "join_request", "Pedido de entrada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="ator",
    )
    action = models.CharField(max_length=32, choices=Action.choices)
    entity_type = models.CharField(max_length=32, choices=EntityType.choices)
    entity_id = models.UUIDField()
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="organização",
    )
    changes = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "registro de auditoria"
        verbose_name_plural = "registros de auditoria"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["entity_type", "entity_id"],
                name="audit_entity_idx",
            ),
            models.Index(fields=["created_at"], name="audit_created_at_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.entity_type}:{self.entity_id}"

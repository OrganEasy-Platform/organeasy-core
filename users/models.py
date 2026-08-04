"""Models de identidade (usuário)."""

from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Usuário do IdP OrganEasy (email como identificador)."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Ativo"
        BLOCKED = "blocked", "Bloqueado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField("e-mail", unique=True)
    full_name = models.CharField("nome completo", max_length=255)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    is_staff = models.BooleanField(
        "acesso ao admin",
        default=False,
        help_text="Permite login no Django Admin.",
    )
    is_active = models.BooleanField(
        "ativo no auth",
        default=True,
        help_text="False bloqueia autenticação (alinhado a status=blocked).",
    )
    date_joined = models.DateTimeField("criado em", default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name = "usuário"
        verbose_name_plural = "usuários"
        ordering = ["email"]

    def __str__(self) -> str:
        return self.email

    def save(self, *args, **kwargs) -> None:
        # status é a fonte de verdade de negócio; is_active sincroniza com o auth Django.
        if self.status == self.Status.BLOCKED:
            self.is_active = False
        elif self.status == self.Status.ACTIVE and not self.is_active:
            self.is_active = True
        super().save(*args, **kwargs)

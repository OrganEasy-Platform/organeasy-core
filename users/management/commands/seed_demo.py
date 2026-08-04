"""Comando para popular dados de demonstração da Fase 2."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from organizations.models import Organization, OrganizationMembership

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Cria superuser demo, 2 organizações e 1 usuário membro de ambas "
        "(senha apenas local; não usar em produção)."
    )

    @transaction.atomic
    def handle(self, *args, **options) -> None:
        admin, created = User.objects.get_or_create(
            email="admin@organeasy.local",
            defaults={
                "full_name": "Admin Demo",
                "is_staff": True,
                "is_superuser": True,
                "status": User.Status.ACTIVE,
            },
        )
        if created:
            admin.set_password("admin-demo-only")
            admin.save()
            self.stdout.write(self.style.SUCCESS("Superuser demo criado."))
        else:
            self.stdout.write("Superuser demo já existia.")

        member, created = User.objects.get_or_create(
            email="membro@organeasy.local",
            defaults={
                "full_name": "Membro Demo",
                "status": User.Status.ACTIVE,
            },
        )
        if created:
            member.set_password("membro-demo-only")
            member.save()
            self.stdout.write(self.style.SUCCESS("Usuário membro demo criado."))
        else:
            self.stdout.write("Usuário membro demo já existia.")

        acme, _ = Organization.objects.get_or_create(
            slug="acme",
            defaults={"name": "Acme Demo", "status": Organization.Status.ACTIVE},
        )
        beta, _ = Organization.objects.get_or_create(
            slug="beta",
            defaults={"name": "Beta Demo", "status": Organization.Status.ACTIVE},
        )

        OrganizationMembership.objects.update_or_create(
            user=member,
            organization=acme,
            defaults={
                "status": OrganizationMembership.Status.ACTIVE,
                "is_default": True,
            },
        )
        OrganizationMembership.objects.update_or_create(
            user=member,
            organization=beta,
            defaults={
                "status": OrganizationMembership.Status.ACTIVE,
                "is_default": False,
            },
        )
        self.stdout.write(self.style.SUCCESS("Organizações e vínculos demo ok."))

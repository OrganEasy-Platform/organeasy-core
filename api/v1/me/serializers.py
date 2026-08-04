"""Serializers do perfil e organizações do usuário autenticado."""

from __future__ import annotations

from rest_framework import serializers

from organizations.models import Organization
from users.models import User


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "status")
        read_only_fields = fields


class MyOrganizationSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.SlugField()
    status = serializers.CharField()
    is_default = serializers.BooleanField()
    membership_status = serializers.CharField()

    @classmethod
    def from_organizations(
        cls,
        organizations: list[Organization],
        flags: dict,
    ) -> list[dict]:
        payload = []
        for org in organizations:
            meta = flags.get(org.id, {"is_default": False, "membership_status": "active"})
            payload.append(
                {
                    "id": org.id,
                    "name": org.name,
                    "slug": org.slug,
                    "status": org.status,
                    "is_default": meta["is_default"],
                    "membership_status": meta["membership_status"],
                }
            )
        return payload

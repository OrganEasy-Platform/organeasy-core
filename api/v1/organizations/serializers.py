"""Serializers do onboarding de organizações (Pacote B)."""

from __future__ import annotations

from rest_framework import serializers

from organizations.models import (
    Organization,
    OrganizationInviteCode,
    OrganizationJoinRequest,
)


class OrganizationCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=100, required=False, allow_blank=False)


class OrganizationOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "slug", "status", "created_at")
        read_only_fields = fields


class TokenPairOutSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    token_type = serializers.CharField()
    expires_in = serializers.IntegerField()


class CreateOrganizationResponseSerializer(serializers.Serializer):
    organization = OrganizationOutSerializer()
    tokens = TokenPairOutSerializer()


class JoinByCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=32)


class JoinByCodeResponseSerializer(serializers.Serializer):
    organization = OrganizationOutSerializer()
    tokens = TokenPairOutSerializer()


class JoinRequestCreateSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=500, required=False, allow_blank=True)


class JoinRequestOutSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_id = serializers.UUIDField(source="user.id", read_only=True)

    class Meta:
        model = OrganizationJoinRequest
        fields = (
            "id",
            "organization",
            "user_id",
            "user_email",
            "status",
            "message",
            "reviewed_by",
            "reviewed_at",
            "created_at",
        )
        read_only_fields = fields


class InviteCodeOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationInviteCode
        fields = (
            "id",
            "code",
            "is_active",
            "expires_at",
            "max_uses",
            "use_count",
            "created_at",
        )
        read_only_fields = fields

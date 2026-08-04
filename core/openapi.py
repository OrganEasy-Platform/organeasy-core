"""Helpers OpenAPI (drf-spectacular) para envelopes padronizados da API."""

from __future__ import annotations

from typing import Any

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers


class SessionAuthentication401Extension(OpenApiAuthenticationExtension):
    """Documenta cookie de sessão no schema OpenAPI."""

    target_class = "core.authentication.SessionAuthentication401"
    name = "cookieAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "sessionid",
        }


def success_envelope(data: Any, *, name: str):
    """Schema do envelope de sucesso: {success, message?, data}."""
    return inline_serializer(
        name=name,
        fields={
            "success": serializers.BooleanField(),
            "message": serializers.CharField(required=False, allow_blank=True),
            "data": data,
        },
    )


def error_envelope(*, name: str = "ErrorEnvelope"):
    """Schema do envelope de erro unificado."""
    return inline_serializer(
        name=name,
        fields={
            "success": serializers.BooleanField(),
            "message": serializers.CharField(),
            "errors": serializers.DictField(required=False),
            "error_code": serializers.CharField(),
        },
    )

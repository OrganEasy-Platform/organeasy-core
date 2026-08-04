"""Serializers do health check (contrato OpenAPI / resposta)."""

from rest_framework import serializers


class HealthCheckSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    service = serializers.CharField()
    status = serializers.CharField()

"""Views de health check da API v1."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.health.serializers import HealthCheckSerializer


@extend_schema(
    tags=["health"],
    summary="Health check",
    description="Readiness/liveness público para orquestração e smoke local.",
    responses={200: HealthCheckSerializer},
)
@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request: Request) -> Response:
    """Health check público para readiness/liveness local e orquestração."""
    return Response(
        {
            "success": True,
            "message": "organeasy-core ok",
            "service": "organeasy-core",
            "status": "healthy",
        },
        status=status.HTTP_200_OK,
    )

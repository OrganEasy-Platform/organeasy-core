"""Views da API do app setup (fundação / health)."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response


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

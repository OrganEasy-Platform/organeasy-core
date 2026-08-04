"""Views do perfil autenticado (Fase 2 — SessionAuthentication)."""

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.me.serializers import MeSerializer, MyOrganizationSerializer
from core.openapi import error_envelope, success_envelope
from core.responses import success_response
from organizations.services import get_membership_flags, list_available_organizations


@extend_schema(
    tags=["me"],
    summary="Perfil do usuário autenticado",
    responses={
        200: success_envelope(MeSerializer(), name="MeSuccessResponse"),
        401: error_envelope(name="MeUnauthorized"),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request: Request) -> Response:
    """Retorna o perfil do usuário autenticado."""
    serializer = MeSerializer(request.user)
    return success_response(serializer.data)


@extend_schema(
    tags=["me"],
    summary="Organizações do usuário autenticado",
    description=(
        "Lista organizações ativas às quais o usuário pertence "
        "(membership com status active)."
    ),
    responses={
        200: success_envelope(
            MyOrganizationSerializer(many=True),
            name="MyOrganizationsSuccessResponse",
        ),
        401: error_envelope(name="MyOrganizationsUnauthorized"),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_organizations(request: Request) -> Response:
    """Lista organizações ativas às quais o usuário pertence (membership ativo)."""
    qs = list_available_organizations(user=request.user)
    organizations = list(qs)
    flags = get_membership_flags(user=request.user, organizations=organizations)
    data = MyOrganizationSerializer.from_organizations(organizations, flags)
    return success_response(data)

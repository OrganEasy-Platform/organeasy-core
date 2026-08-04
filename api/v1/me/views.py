"""Views do perfil autenticado (Fase 2 — SessionAuthentication)."""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.me.serializers import MeSerializer, MyOrganizationSerializer
from core.responses import success_response
from organizations.services import get_membership_flags, list_available_organizations


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request: Request) -> Response:
    """Retorna o perfil do usuário autenticado."""
    serializer = MeSerializer(request.user)
    return success_response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_organizations(request: Request) -> Response:
    """Lista organizações ativas às quais o usuário pertence (membership ativo)."""
    qs = list_available_organizations(user=request.user)
    organizations = list(qs)
    flags = get_membership_flags(user=request.user, organizations=organizations)
    data = MyOrganizationSerializer.from_organizations(organizations, flags)
    return success_response(data)

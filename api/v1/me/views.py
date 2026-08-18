"""Views do perfil autenticado (JWT Bearer ou Session)."""

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.me.serializers import MeSerializer, MyOrganizationSerializer
from core.openapi import error_envelope, success_envelope
from core.responses import success_response
from organizations.models import Organization, OrganizationMembership
from organizations.services import get_membership_flags, list_available_organizations


def _active_organization_from_request(request: Request) -> dict | None:
    """Resolve org ativa a partir do claim org_id do access JWT (Session → null)."""
    token = request.auth
    if token is None or not hasattr(token, "get"):
        return None
    org_id = token.get("org_id")
    if not org_id:
        return None
    membership = (
        OrganizationMembership.objects.select_related("organization")
        .filter(
            user=request.user,
            organization_id=org_id,
            status=OrganizationMembership.Status.ACTIVE,
            organization__status=Organization.Status.ACTIVE,
        )
        .first()
    )
    if membership is None:
        return None
    org = membership.organization
    return {"id": org.id, "name": org.name, "slug": org.slug}


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
    """Retorna o perfil do usuário autenticado e a organização ativa do token."""
    data = MeSerializer(request.user).data
    data["active_organization"] = _active_organization_from_request(request)
    return success_response(data)


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

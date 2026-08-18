"""Views FBV de autenticação JWT (login / refresh / logout / switch)."""

from __future__ import annotations

import logging

from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from api.v1.auth.serializers import (
    LoginSerializer,
    LogoutSerializer,
    RefreshSerializer,
    SwitchOrganizationSerializer,
    TokenPairSerializer,
)
from api.v1.auth.services import switch_active_organization
from core.openapi import error_envelope, success_envelope
from core.responses import error_response, success_response
from organizations.services import (
    OrganizationMembershipLostError,
    OrganizationNotAllowedError,
)

logger = logging.getLogger(__name__)


def _auth_failure(message: str) -> Response:
    return error_response(
        message=message,
        error_code="AUTHENTICATION_REQUIRED",
        status=status.HTTP_401_UNAUTHORIZED,
    )


def _organization_not_allowed(message: str = "Organização não permitida para este usuário.") -> Response:
    return error_response(
        message=message,
        error_code="ORGANIZATION_NOT_ALLOWED",
        status=status.HTTP_403_FORBIDDEN,
    )


def _membership_lost(message: str) -> Response:
    return error_response(
        message=message,
        error_code="ORGANIZATION_MEMBERSHIP_LOST",
        status=status.HTTP_403_FORBIDDEN,
    )


def _first_error_message(errors: dict) -> str | None:
    for key in (
        "detail",
        "non_field_errors",
        "refresh",
        "email",
        "password",
        "organization_id",
    ):
        value = errors.get(key)
        if value is None:
            continue
        if isinstance(value, list) and value:
            return str(value[0])
        return str(value)
    return None


def _org_id_from_auth(request: Request) -> str | None:
    token = request.auth
    if token is None:
        return None
    org_id = token.get("org_id") if hasattr(token, "get") else None
    if org_id is None or org_id == "":
        return None
    return str(org_id)


@extend_schema(
    tags=["auth"],
    summary="Login (obter access e refresh JWT)",
    request=LoginSerializer,
    responses={
        200: success_envelope(TokenPairSerializer(), name="LoginSuccessResponse"),
        400: error_envelope(name="LoginValidationError"),
        401: error_envelope(name="LoginUnauthorized"),
        403: error_envelope(name="LoginOrganizationForbidden"),
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request: Request) -> Response:
    """Valida email/senha, resolve org ativa e emite par de tokens JWT."""
    serializer = LoginSerializer(data=request.data, context={"request": request})
    try:
        if not serializer.is_valid():
            if serializer.auth_failed:
                logger.info("login_failed reason=invalid_credentials")
                return _auth_failure(
                    _first_error_message(serializer.errors) or "Credenciais inválidas."
                )
            return Response(
                {
                    "success": False,
                    "message": "Erro de validação.",
                    "errors": serializer.errors,
                    "error_code": "VALIDATION_ERROR",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
    except OrganizationNotAllowedError as exc:
        logger.info("login_failed reason=organization_not_allowed")
        return _organization_not_allowed(str(exc))

    tokens = serializer.create_tokens()
    user = serializer.validated_data["user"]
    organization = serializer.validated_data.get("organization")
    logger.info(
        "login_success user_id=%s org_id=%s source=%s",
        user.pk,
        organization.pk if organization else None,
        serializer.validated_data.get("org_resolve_source"),
    )
    return success_response(tokens)


@extend_schema(
    tags=["auth"],
    summary="Refresh JWT (rotação + blacklist do refresh anterior)",
    request=RefreshSerializer,
    responses={
        200: success_envelope(TokenPairSerializer(), name="RefreshSuccessResponse"),
        400: error_envelope(name="RefreshValidationError"),
        401: error_envelope(name="RefreshUnauthorized"),
        403: error_envelope(name="RefreshMembershipLost"),
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def refresh(request: Request) -> Response:
    """Emite novo access/refresh; o refresh enviado é blacklisted (rotação)."""
    serializer = RefreshSerializer(data=request.data)
    if not serializer.is_valid():
        logger.info("refresh_failed reason=invalid_or_expired")
        return _auth_failure(
            _first_error_message(serializer.errors)
            or "Refresh token inválido ou expirado."
        )
    try:
        tokens = serializer.create_tokens()
    except OrganizationMembershipLostError as exc:
        logger.info("refresh_failed reason=membership_lost")
        return _membership_lost(str(exc))
    except (TokenError, InvalidToken):
        logger.info("refresh_failed reason=token_error")
        return _auth_failure("Refresh token inválido ou expirado.")
    logger.info("refresh_success")
    return success_response(tokens)


@extend_schema(
    tags=["auth"],
    summary="Logout (blacklist do refresh token)",
    description="Requer Bearer access token válido. O refresh informado entra na blacklist.",
    request=LogoutSerializer,
    responses={
        200: inline_serializer(
            name="LogoutSuccessResponse",
            fields={
                "success": serializers.BooleanField(),
                "message": serializers.CharField(),
            },
        ),
        400: error_envelope(name="LogoutValidationError"),
        401: error_envelope(name="LogoutUnauthorized"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request: Request) -> Response:
    """Revoga o refresh token informado (blacklist)."""
    serializer = LogoutSerializer(data=request.data)
    if not serializer.is_valid():
        logger.info("logout_failed reason=invalid_refresh")
        return _auth_failure(
            _first_error_message(serializer.errors)
            or "Refresh token inválido ou já revogado."
        )
    try:
        serializer.save()
    except TokenError:
        logger.info("logout_failed reason=blacklist_error")
        return _auth_failure("Refresh token inválido ou já revogado.")
    logger.info("logout_success user_id=%s", request.user.pk)
    return success_response(message="Logout realizado com sucesso.")


@extend_schema(
    tags=["auth"],
    summary="Trocar organização ativa (nova pair JWT)",
    description=(
        "Requer Bearer access. Valida membership ativo; emite nova pair com "
        "`org_id` da organização alvo. Se `refresh` for enviado, entra na blacklist."
    ),
    request=SwitchOrganizationSerializer,
    responses={
        200: success_envelope(TokenPairSerializer(), name="SwitchOrgSuccessResponse"),
        400: error_envelope(name="SwitchOrgValidationError"),
        401: error_envelope(name="SwitchOrgUnauthorized"),
        403: error_envelope(name="SwitchOrgForbidden"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def switch_organization(request: Request) -> Response:
    """Troca o contexto de tenant e emite nova pair de tokens."""
    serializer = SwitchOrganizationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {
                "success": False,
                "message": "Erro de validação.",
                "errors": serializer.errors,
                "error_code": "VALIDATION_ERROR",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    refresh_raw = serializer.validated_data.get("refresh")
    from_org_id = _org_id_from_auth(request)
    try:
        tokens = switch_active_organization(
            user=request.user,
            organization_id=serializer.validated_data["organization_id"],
            from_org_id=from_org_id,
            refresh_raw=refresh_raw,
        )
    except OrganizationNotAllowedError as exc:
        logger.info(
            "switch_failed reason=organization_not_allowed user_id=%s",
            request.user.pk,
        )
        return _organization_not_allowed(str(exc))
    except TokenError:
        logger.info("switch_failed reason=invalid_refresh user_id=%s", request.user.pk)
        return _auth_failure("Refresh token inválido ou já revogado.")

    logger.info(
        "switch_success user_id=%s from_org_id=%s to_org_id=%s",
        request.user.pk,
        from_org_id,
        serializer.validated_data["organization_id"],
    )
    return success_response(tokens)

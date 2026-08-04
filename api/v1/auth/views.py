"""Views FBV de autenticação JWT (login / refresh / logout)."""

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
    TokenPairSerializer,
)
from core.openapi import error_envelope, success_envelope
from core.responses import error_response, success_response

logger = logging.getLogger(__name__)


def _auth_failure(message: str) -> Response:
    return error_response(
        message=message,
        error_code="AUTHENTICATION_REQUIRED",
        status=status.HTTP_401_UNAUTHORIZED,
    )


def _first_error_message(errors: dict) -> str | None:
    for key in ("detail", "non_field_errors", "refresh", "email", "password"):
        value = errors.get(key)
        if value is None:
            continue
        if isinstance(value, list) and value:
            return str(value[0])
        return str(value)
    return None


@extend_schema(
    tags=["auth"],
    summary="Login (obter access e refresh JWT)",
    request=LoginSerializer,
    responses={
        200: success_envelope(TokenPairSerializer(), name="LoginSuccessResponse"),
        400: error_envelope(name="LoginValidationError"),
        401: error_envelope(name="LoginUnauthorized"),
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request: Request) -> Response:
    """Valida email/senha e emite par de tokens JWT."""
    serializer = LoginSerializer(data=request.data, context={"request": request})
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
    tokens = serializer.create_tokens()
    logger.info("login_success user_id=%s", serializer.validated_data["user"].pk)
    return success_response(tokens)


@extend_schema(
    tags=["auth"],
    summary="Refresh JWT (rotação + blacklist do refresh anterior)",
    request=RefreshSerializer,
    responses={
        200: success_envelope(TokenPairSerializer(), name="RefreshSuccessResponse"),
        400: error_envelope(name="RefreshValidationError"),
        401: error_envelope(name="RefreshUnauthorized"),
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

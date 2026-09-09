"""Views FBV de onboarding de organizações (Pacote B)."""

from __future__ import annotations

import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from api.v1.organizations.serializers import (
    CreateOrganizationResponseSerializer,
    InviteCodeOutSerializer,
    JoinByCodeResponseSerializer,
    JoinByCodeSerializer,
    JoinRequestCreateSerializer,
    JoinRequestOutSerializer,
    OrganizationCreateSerializer,
)
from core.openapi import error_envelope, success_envelope
from core.responses import error_response, success_response
from organizations.services.exceptions import (
    AlreadyMemberError,
    InviteCodeInvalidError,
    JoinRequestAlreadyPendingError,
    JoinRequestInvalidStateError,
    OrgCreateLimitReachedError,
)
from organizations.services.invite_service import (
    create_invite_code,
    deactivate_invite_code,
    list_invite_codes,
    redeem_invite_code,
)
from organizations.services.join_request_service import (
    approve_join_request,
    cancel_join_request,
    create_join_request,
    list_join_requests,
    reject_join_request,
)
from organizations.services.onboarding_service import create_organization
from organizations.services.tenant_service import OrganizationNotAllowedError

logger = logging.getLogger(__name__)


def _forbidden(message: str, error_code: str) -> Response:
    return error_response(
        message=message,
        error_code=error_code,
        status=status.HTTP_403_FORBIDDEN,
    )


def _conflict(message: str, error_code: str) -> Response:
    return error_response(
        message=message,
        error_code=error_code,
        status=status.HTTP_409_CONFLICT,
    )


@extend_schema(
    tags=["organizations"],
    summary="Criar organização",
    request=OrganizationCreateSerializer,
    responses={
        201: success_envelope(
            CreateOrganizationResponseSerializer(),
            name="CreateOrganizationSuccess",
        ),
        400: error_envelope(name="CreateOrganizationValidation"),
        401: error_envelope(name="CreateOrganizationUnauthorized"),
        403: error_envelope(name="CreateOrganizationForbidden"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def organization_create(request: Request) -> Response:
    serializer = OrganizationCreateSerializer(data=request.data)
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
    try:
        result = create_organization(
            user=request.user,
            name=serializer.validated_data["name"],
            slug=serializer.validated_data.get("slug"),
        )
    except OrgCreateLimitReachedError as exc:
        logger.info("org_create_failed reason=limit user_id=%s", request.user.pk)
        return _forbidden(str(exc), "ORG_CREATE_LIMIT_REACHED")

    org = result["organization"]
    logger.info("org_create_success user_id=%s org_id=%s", request.user.pk, org.pk)
    return success_response(
        {
            "organization": {
                "id": org.id,
                "name": org.name,
                "slug": org.slug,
                "status": org.status,
                "created_at": org.created_at,
            },
            "tokens": result["tokens"],
        },
        status=status.HTTP_201_CREATED,
    )


@extend_schema(
    tags=["organizations"],
    summary="Entrar em organização via código de convite",
    request=JoinByCodeSerializer,
    responses={
        200: success_envelope(
            JoinByCodeResponseSerializer(),
            name="JoinByCodeSuccess",
        ),
        400: error_envelope(name="JoinByCodeValidation"),
        401: error_envelope(name="JoinByCodeUnauthorized"),
        403: error_envelope(name="JoinByCodeForbidden"),
        409: error_envelope(name="JoinByCodeConflict"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_by_code(request: Request) -> Response:
    serializer = JoinByCodeSerializer(data=request.data)
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
    try:
        result = redeem_invite_code(
            user=request.user,
            code=serializer.validated_data["code"],
        )
    except InviteCodeInvalidError as exc:
        return _forbidden(str(exc), "INVITE_CODE_INVALID")
    except AlreadyMemberError as exc:
        return _conflict(str(exc), "ALREADY_MEMBER")

    org = result["organization"]
    logger.info(
        "join_by_code_success user_id=%s org_id=%s",
        request.user.pk,
        org.pk,
    )
    return success_response(
        {
            "organization": {
                "id": org.id,
                "name": org.name,
                "slug": org.slug,
                "status": org.status,
                "created_at": org.created_at,
            },
            "tokens": result["tokens"],
        }
    )


@extend_schema(
    tags=["organizations"],
    summary="Listar ou criar pedidos de entrada",
    request=JoinRequestCreateSerializer,
    responses={
        200: success_envelope(
            JoinRequestOutSerializer(many=True),
            name="JoinRequestListSuccess",
        ),
        201: success_envelope(JoinRequestOutSerializer(), name="JoinRequestCreateSuccess"),
        400: error_envelope(name="JoinRequestValidation"),
        401: error_envelope(name="JoinRequestUnauthorized"),
        403: error_envelope(name="JoinRequestForbidden"),
        409: error_envelope(name="JoinRequestConflict"),
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def join_requests(request: Request, organization_id) -> Response:
    if request.method == "GET":
        status_filter = request.query_params.get("status")
        try:
            qs = list_join_requests(
                user=request.user,
                organization_id=organization_id,
                status=status_filter,
            )
        except OrganizationNotAllowedError as exc:
            return _forbidden(str(exc), "ORGANIZATION_NOT_ALLOWED")
        return success_response(JoinRequestOutSerializer(qs, many=True).data)

    serializer = JoinRequestCreateSerializer(data=request.data)
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
    try:
        join_request = create_join_request(
            user=request.user,
            organization_id=organization_id,
            message=serializer.validated_data.get("message", ""),
        )
    except OrganizationNotAllowedError as exc:
        return _forbidden(str(exc), "ORGANIZATION_NOT_ALLOWED")
    except AlreadyMemberError as exc:
        return _conflict(str(exc), "ALREADY_MEMBER")
    except JoinRequestAlreadyPendingError as exc:
        return _conflict(str(exc), "JOIN_REQUEST_ALREADY_PENDING")

    return success_response(
        JoinRequestOutSerializer(join_request).data,
        status=status.HTTP_201_CREATED,
    )


@extend_schema(
    tags=["organizations"],
    summary="Aprovar pedido de entrada",
    responses={
        200: success_envelope(JoinRequestOutSerializer(), name="JoinRequestApproveSuccess"),
        401: error_envelope(name="JoinRequestApproveUnauthorized"),
        403: error_envelope(name="JoinRequestApproveForbidden"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_request_approve(request: Request, organization_id, request_id) -> Response:
    try:
        join_request = approve_join_request(
            reviewer=request.user,
            organization_id=organization_id,
            request_id=request_id,
        )
    except OrganizationNotAllowedError as exc:
        return _forbidden(str(exc), "ORGANIZATION_NOT_ALLOWED")
    except JoinRequestInvalidStateError as exc:
        return _forbidden(str(exc), "JOIN_REQUEST_INVALID")
    return success_response(JoinRequestOutSerializer(join_request).data)


@extend_schema(
    tags=["organizations"],
    summary="Rejeitar pedido de entrada",
    responses={
        200: success_envelope(JoinRequestOutSerializer(), name="JoinRequestRejectSuccess"),
        401: error_envelope(name="JoinRequestRejectUnauthorized"),
        403: error_envelope(name="JoinRequestRejectForbidden"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_request_reject(request: Request, organization_id, request_id) -> Response:
    try:
        join_request = reject_join_request(
            reviewer=request.user,
            organization_id=organization_id,
            request_id=request_id,
        )
    except OrganizationNotAllowedError as exc:
        return _forbidden(str(exc), "ORGANIZATION_NOT_ALLOWED")
    except JoinRequestInvalidStateError as exc:
        return _forbidden(str(exc), "JOIN_REQUEST_INVALID")
    return success_response(JoinRequestOutSerializer(join_request).data)


@extend_schema(
    tags=["organizations"],
    summary="Cancelar próprio pedido de entrada",
    responses={
        200: success_envelope(JoinRequestOutSerializer(), name="JoinRequestCancelSuccess"),
        401: error_envelope(name="JoinRequestCancelUnauthorized"),
        403: error_envelope(name="JoinRequestCancelForbidden"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_request_cancel(request: Request, request_id) -> Response:
    try:
        join_request = cancel_join_request(user=request.user, request_id=request_id)
    except JoinRequestInvalidStateError as exc:
        return _forbidden(str(exc), "JOIN_REQUEST_INVALID")
    return success_response(JoinRequestOutSerializer(join_request).data)


@extend_schema(
    tags=["organizations"],
    summary="Listar ou gerar códigos de convite",
    responses={
        200: success_envelope(
            InviteCodeOutSerializer(many=True),
            name="InviteCodeListSuccess",
        ),
        201: success_envelope(InviteCodeOutSerializer(), name="InviteCodeCreateSuccess"),
        401: error_envelope(name="InviteCodeUnauthorized"),
        403: error_envelope(name="InviteCodeForbidden"),
    },
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def invite_codes(request: Request, organization_id) -> Response:
    if request.method == "GET":
        try:
            qs = list_invite_codes(user=request.user, organization_id=organization_id)
        except OrganizationNotAllowedError as exc:
            return _forbidden(str(exc), "ORGANIZATION_NOT_ALLOWED")
        return success_response(InviteCodeOutSerializer(qs, many=True).data)

    try:
        invite = create_invite_code(user=request.user, organization_id=organization_id)
    except OrganizationNotAllowedError as exc:
        return _forbidden(str(exc), "ORGANIZATION_NOT_ALLOWED")
    return success_response(
        InviteCodeOutSerializer(invite).data,
        status=status.HTTP_201_CREATED,
    )


@extend_schema(
    tags=["organizations"],
    summary="Desativar código de convite",
    responses={
        200: success_envelope(InviteCodeOutSerializer(), name="InviteCodeDeactivateSuccess"),
        401: error_envelope(name="InviteCodeDeactivateUnauthorized"),
        403: error_envelope(name="InviteCodeDeactivateForbidden"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def invite_code_deactivate(request: Request, organization_id, invite_id) -> Response:
    try:
        invite = deactivate_invite_code(
            user=request.user,
            organization_id=organization_id,
            invite_id=invite_id,
        )
    except OrganizationNotAllowedError as exc:
        return _forbidden(str(exc), "ORGANIZATION_NOT_ALLOWED")
    except InviteCodeInvalidError as exc:
        return _forbidden(str(exc), "INVITE_CODE_INVALID")
    return success_response(InviteCodeOutSerializer(invite).data)

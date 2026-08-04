"""Exception handler DRF com formato unificado."""

from __future__ import annotations

from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def unified_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Converte exceções DRF para o envelope {success, message, errors, error_code}."""
    response = exception_handler(exc, context)
    if response is None:
        return None

    errors = response.data
    if isinstance(errors, dict):
        message = str(errors.get("detail", "Erro na requisição."))
        if "detail" in errors and len(errors) == 1:
            payload_errors: dict[str, Any] = {}
        else:
            payload_errors = {
                key: value for key, value in errors.items() if key != "detail"
            }
            if "detail" not in errors:
                message = "Erro de validação."
    elif isinstance(errors, list):
        message = str(errors[0]) if errors else "Erro na requisição."
        payload_errors = {"non_field_errors": errors}
    else:
        message = str(errors)
        payload_errors = {}

    status_code = response.status_code
    error_code = {
        status.HTTP_400_BAD_REQUEST: "VALIDATION_ERROR",
        status.HTTP_401_UNAUTHORIZED: "AUTHENTICATION_REQUIRED",
        status.HTTP_403_FORBIDDEN: "PERMISSION_DENIED",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_409_CONFLICT: "CONFLICT",
    }.get(status_code, "ERROR")

    response.data = {
        "success": False,
        "message": message,
        "errors": payload_errors,
        "error_code": error_code,
    }
    return response

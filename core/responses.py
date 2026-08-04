"""Respostas padronizadas da API."""

from __future__ import annotations

from typing import Any

from rest_framework.response import Response


def success_response(
    data: Any = None,
    *,
    message: str = "",
    status: int = 200,
) -> Response:
    """Envelope de sucesso: {success, message?, data?}."""
    payload: dict[str, Any] = {"success": True}
    if message:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    return Response(payload, status=status)


def error_response(
    *,
    message: str,
    errors: dict[str, Any] | None = None,
    error_code: str = "ERROR",
    status: int = 400,
) -> Response:
    """Envelope de erro alinhado a docs/cursor/drf-reference.md."""
    return Response(
        {
            "success": False,
            "message": message,
            "errors": errors or {},
            "error_code": error_code,
        },
        status=status,
    )

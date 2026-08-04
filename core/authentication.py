"""Autenticação Session que emite 401 (em vez de 403) para anônimos."""

from rest_framework.authentication import SessionAuthentication


class SessionAuthentication401(SessionAuthentication):
    """
    SessionAuthentication padrão do DRF omite WWW-Authenticate e vira 403.

    Expor um challenge faz o DRF responder 401 Unauthorized, alinhado ao
    contrato da API (JWT + sessão Admin/dev).
    """

    def authenticate_header(self, request) -> str:
        return "Session"

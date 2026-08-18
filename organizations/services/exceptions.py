"""Exceções de domínio do onboarding de organizações (Pacote B)."""

from __future__ import annotations


class OrgCreateLimitReachedError(Exception):
    """Usuário atingiu ORG_CREATE_LIMIT de organizações criadas."""


class InviteCodeInvalidError(Exception):
    """Código inexistente, inativo, expirado ou esgotado."""


class AlreadyMemberError(Exception):
    """Usuário já possui membership active na organização."""


class JoinRequestAlreadyPendingError(Exception):
    """Já existe pedido pending para o par user/org."""


class JoinRequestInvalidStateError(Exception):
    """Pedido não está no estado esperado para a ação."""

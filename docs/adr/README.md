# Architecture Decision Records (ADRs)

Decisões estruturais do `organeasy-core` e da plataforma OrganEasy, no que afeta este repositório.

| ADR | Título | Status |
| --- | ------ | ------ |
| [0001](0001-django-as-idp.md) | Django como Identity Provider (IdP) | Aceito |
| [0002](0002-multi-tenancy-by-column.md) | Multi-tenancy lógico por coluna (`organization_id`) | Aceito |
| [0003](0003-jwt-minimal-claims.md) | Claims JWT mínimas | Aceito |
| [0004](0004-sync-communication-first.md) | Comunicação síncrona agora; eventos/outbox depois | Aceito |

## Formato

Cada ADR registra contexto, decisão, alternativas consideradas e consequências.

Fonte de produto e fases: [OrganEasy_Plano_de_Implementacao_Revisado.md](../initial_plan/OrganEasy_Plano_de_Implementacao_Revisado.md).

Nota sobre o roadmap antigo: [roadmap-reconciliation.md](../initial_plan/roadmap-reconciliation.md).

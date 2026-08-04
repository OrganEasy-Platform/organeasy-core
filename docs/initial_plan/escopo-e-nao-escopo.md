# Escopo e não-escopo — organeasy-core

Documento de limites do repositório `organeasy-core` (serviço de identidade da plataforma OrganEasy).

**Fontes:** [OrganEasy_Plano_de_Implementacao_Revisado.md](OrganEasy_Plano_de_Implementacao_Revisado.md) · plano inicial de execução no Cursor · [ADRs](../adr/README.md).

## Visão em menos de dois minutos

O OrganEasy é uma plataforma SaaS multi-organização. Este repositório **não** é o ERP completo: é o **núcleo de identidade**. Django + DRF + SimpleJWT cuidam de usuários, organizações, JWT, papéis e módulos habilitados. Módulos de negócio (Kanban, Financeiro, etc.) serão serviços separados (tipicamente FastAPI) que **consomem** o token emitido aqui.

## Escopo deste repositório (MVP Foundation)

| Área | Inclui |
| ---- | ------ |
| Identidade | User (estados ativo/bloqueado), Organization, vínculo User↔Organization |
| Auth | Login, refresh, logout, `me`; access curto + refresh com rotação/blacklist |
| Tenant | Organização ativa, `org_id` no JWT, isolamento por coluna |
| RBAC | Papéis/scopes por organização |
| Módulos | Catálogo e habilitação por organização (feature flags) |
| Admin | Django Admin para operações administrativas |
| Auditoria | Alterações administrativas e concessões sensíveis |
| Fundação | Settings por ambiente, Docker Compose, CI, docs/ADRs |

Marco público recomendado: **v0.1.0 / Foundation** quando as fases 0–3 (idealmente até 6) estiverem demonstráveis.

## Classificação de capacidades da plataforma

| Capacidade | Classificação | Onde |
| ---------- | ------------- | ---- |
| IdP Django (users, orgs, JWT, RBAC, módulos) | **MVP deste repo** | `organeasy-core` |
| Docker Compose + PostgreSQL + Redis + CI | **MVP deste repo** (Fase 1) | `organeasy-core` |
| Kanban | Posterior (módulo FastAPI) | Fora deste repo (por enquanto) |
| Chat / notificações / agenda | Posterior | Fora |
| Financeiro / RH / WMS / TMS / E-commerce | Posterior / fora do MVP do core | Fora |
| Docker Swarm, HAProxy, stack completa de observabilidade | Depois do core estável | Infra plataforma |
| Frontend de produto | Fora (exceto Django Admin) | Outro repositório |
| Chamadas de vídeo, folha completa, contabilidade fiscal | **Fora de escopo** do MVP | — |

## Não-escopo explícito (este plano / este repo)

- Implementar Kanban, Chat, Financeiro, RH, WMS, TMS ou E-commerce **neste** repositório
- Apresentar o README como se o ERP completo já existisse
- Monorepo da plataforma inteira (decisão futura; hoje o escopo é só `organeasy-core`)
- JWKS/RS256 completo sem consumidor FastAPI (preparar caminho; não bloquear o protótipo HS256 local)
- Mensageria/outbox como pré-requisito das Fases 0–6 (ver [ADR 0004](../adr/0004-sync-communication-first.md))

## Decisões travadas

| Decisão | Referência |
| -------- | ----------- |
| Django como IdP | [ADR 0001](../adr/0001-django-as-idp.md) |
| Multi-tenancy por coluna | [ADR 0002](../adr/0002-multi-tenancy-by-column.md) |
| Claims JWT mínimas | [ADR 0003](../adr/0003-jwt-minimal-claims.md) |
| Sync agora; eventos depois | [ADR 0004](../adr/0004-sync-communication-first.md) |
| Views API = FBV `@api_view` | Rules do projeto / `docs/cursor/drf-reference.md` |
| Models/endpoints novos só com aprovação | Rule `007` + skill `new-feature-design` |

## Ordem obrigatória das fases neste repo

`0 (docs) → 1 (Docker/CI/Postgres) → 2 (User/Org) → 3 (JWT) → 4 (tenant) → 5 (RBAC) → 6 (módulos)`

Backlog macro: [backlog-macro.md](backlog-macro.md).

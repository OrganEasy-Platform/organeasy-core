# organeasy-core

Serviço de **identidade** da plataforma SaaS OrganEasy: autenticação, usuários, organizações (multi-tenancy), permissões, módulos habilitados, auditoria e Django Admin.

Não é o ERP completo. Módulos de negócio (Kanban, Financeiro, RH, etc.) ficam em serviços separados e consomem o JWT emitido aqui.

## Visão (elevator pitch)

OrganEasy é uma plataforma SaaS multi-organização. O `organeasy-core` é o Identity Provider: Django + DRF + SimpleJWT centralizam login, tenant, papéis e o catálogo de módulos. Outros serviços validam o token e aplicam regras de domínio — sem reinventar autenticação.

## Escopo e não-escopo

| No escopo deste repo (MVP Foundation) | Fora deste repo / fora do MVP do core |
| ------------------------------------- | ------------------------------------- |
| Users, organizations, vínculo, Admin | Kanban, Chat, Financeiro, RH, WMS, TMS, E-commerce |
| JWT (login/refresh/logout/me), claims mínimas | Frontend de produto (além do Admin) |
| Tenant por coluna + `org_id` no token | Docker Swarm, HAProxy, observabilidade completa |
| RBAC e módulos habilitáveis por org | Chamadas de vídeo, folha completa, contabilidade fiscal |
| Docker Compose, CI, ADRs | Monorepo da plataforma inteira (decisão futura) |

Detalhes: [docs/initial_plan/escopo-e-nao-escopo.md](docs/initial_plan/escopo-e-nao-escopo.md).

## Stack (deste repositório)

- Django + Django REST Framework
- SimpleJWT (login/refresh/logout; claims mínimas)
- PostgreSQL via Docker Compose (SQLite opcional para smoke local)
- Redis (cache; LocMem se `REDIS_URL` vazio)
- Celery quando houver tarefa assíncrona justificada
- CI GitHub Actions (ruff + pytest unitário)

## Decisões travadas (ADRs)

| ADR | Decisão |
| --- | -------- |
| [0001](docs/adr/0001-django-as-idp.md) | Django como IdP |
| [0002](docs/adr/0002-multi-tenancy-by-column.md) | Multi-tenancy por coluna |
| [0003](docs/adr/0003-jwt-minimal-claims.md) | Claims JWT mínimas (`sub`, `org_id`, `roles`/`scopes`, `iss`, `aud`, `jti`) |
| [0004](docs/adr/0004-sync-communication-first.md) | Comunicação síncrona agora; eventos/outbox depois |

Índice: [docs/adr/README.md](docs/adr/README.md).

## Documentação de planejamento

| Doc | Uso |
| --- | --- |
| [OpenAPI / Swagger](docs/api/openapi.md) | Schema, `/api/docs/`, como documentar endpoints |
| [Plano de implementação revisado](docs/initial_plan/OrganEasy_Plano_de_Implementacao_Revisado.md) | Documento mestre (fases e arquitetura) |
| [Reconciliação do roadmap antigo](docs/initial_plan/roadmap-reconciliation.md) | FastAPI antigo vs Django IdP |
| [Backlog macro](docs/initial_plan/backlog-macro.md) | Épicos 0–6 (User/Org → JWT → tenant → RBAC → módulos) |
| [Roadmap estratégico (histórico)](docs/initial_plan/OrganEasy_Roadmap_Estrategico.md) | Visão ampla; stack do núcleo desatualizada |

## Estado atual

Já existe:

- Projeto Django com settings por ambiente (`config/settings/`)
- Health check `GET /api/v1/health/`
- Apps `users` / `organizations` / `core` (User, Organization, Membership, AuditLog)
- SimpleJWT: `POST /api/v1/auth/login|refresh|logout|switch-organization/` + Bearer em `/me`
- API `GET /api/v1/me/` (com `active_organization`) e `GET /api/v1/me/organizations/` (JWT ou Session)
- OpenAPI/Swagger (`drf-spectacular`): `GET /api/docs/` e `GET /api/schema/`
- Django Admin para user/org/vínculo com auditoria administrativa
- Docker Compose (Django + PostgreSQL + Redis), Dockerfile e CI GitHub Actions
- PostgreSQL/Redis via env; SQLite só com `DJANGO_DB_ENGINE=sqlite`
- CORS (`django-cors-headers`) e cache Redis/LocMem
- Rules/skills Cursor e `.env.example`

Ainda não (após Fase 4): onboarding criar/entrar org (Pacote B), RBAC (Fase 5), catálogo de módulos (Fase 6).

## Estrutura

```text
config/          # Projeto Django (settings por ambiente, urls, wsgi/asgi)
users/           # User customizado (email) + seed_demo
organizations/   # Organization + OrganizationMembership
core/            # AuditLog, responses, exception handler, tokens JWT
api/v1/          # Endpoints versionados (FBV + path): health, auth, me
docker/          # entrypoint do container web
docs/adr/        # Architecture Decision Records
docs/api/        # OpenAPI/Swagger e contratos de API
docs/identity/   # Modelo de identidade + contrato JWT
docs/initial_plan/
.github/workflows/
manage.py
Dockerfile
docker-compose.yml
```

## Setup local (sem Docker)

```bash
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
copy .env.example .env
# Smoke: deixe DJANGO_DB_ENGINE=sqlite no .env
python manage.py migrate
python manage.py runserver
```

Health check: `GET http://127.0.0.1:8000/api/v1/health/`

Swagger UI: `http://127.0.0.1:8000/api/docs/` · schema OpenAPI: `http://127.0.0.1:8000/api/schema/`

Guia: [docs/api/openapi.md](docs/api/openapi.md).

Após migrate, opcional:

```bash
python manage.py seed_demo
```

Perfil (JWT Bearer ou sessão): `GET /api/v1/me/` · organizações: `GET /api/v1/me/organizations/`

Login JWT:

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"membro@organeasy.local\",\"password\":\"...\"}"
```

Modelo de identidade: [docs/identity/modelo-identidade.md](docs/identity/modelo-identidade.md) · contrato JWT: [docs/identity/jwt-contract.md](docs/identity/jwt-contract.md).

## Docker Compose (recomendado)

Requer Docker Desktop (ou engine + Compose). O Compose sobe `web`, `db` (Postgres 16) e `redis` (7), aplica migrations e expõe a API na porta 8000.

```bash
copy .env.example .env
docker compose up --build
```

Health check: `GET http://127.0.0.1:8000/api/v1/health/`

Variáveis relevantes (ver `.env.example`):

| Variável | Exemplo | Uso |
| -------- | ------- | --- |
| `DJANGO_DB_ENGINE` | `postgresql` ou `sqlite` | Engine do banco |
| `POSTGRES_*` | `organeasy` / host `db` no Compose | Credenciais Postgres |
| `REDIS_URL` | `redis://redis:6379/0` | Cache Redis (vazio = LocMem) |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000` | Origens CORS |
| `DJANGO_ENABLE_API_DOCS` | `true` / `false` | Liga `/api/docs/` e `/api/schema/` (default off em produção) |
| `JWT_ACCESS_LIFETIME_SECONDS` | `900` | Lifetime do access token |
| `JWT_REFRESH_LIFETIME_SECONDS` | `604800` | Lifetime do refresh token |
| `JWT_SIGNING_KEY` | (vazio = `DJANGO_SECRET_KEY`) | Chave HS256 |
| `JWT_ISSUER` / `JWT_AUDIENCE` | `organeasy-auth` / `organeasy-services` | Claims `iss` / `aud` |

## CI

Pipeline em `.github/workflows/ci.yml` (push/PR em `main`/`master`/`develop`):

1. Verifica UTF-8 em `requirements*.txt`
2. `ruff check .`
3. `makemigrations --check --dry-run`
4. `pytest -m "not integration"` (Postgres service no Actions)

Localmente:

```bash
pip install -r requirements-dev.txt
ruff check .
pytest -m "not integration" -v
```

## Alterações recentes

| Data | Tipo | Módulo/Pasta | Alteração | Impacto |
| ---- | ---- | ------------ | --------- | ------- |
| 2026-08-17 | Adicionado | `auth`/`organizations`/`me`, `docs/identity` | Fase 4 Pacote A: `org_id` no JWT, login com org opcional, switch-organization, refresh com revalidação, `/me.active_organization`, helpers de tenant, AuditLog `switch_context`. | Consumidores leem tenant do token; onboarding self-service fica no Pacote B. |
| 2026-08-03 | Adicionado | `api/v1/auth/`, `core/tokens.py`, SimpleJWT | Fase 3: login/refresh/logout JWT, claims ADR 0003 (`org_id` null), blacklist, contrato em `docs/identity/jwt-contract.md`. | IdP emite Bearer; `/me` aceita JWT; refresh rotacionado e revogável. |
| 2026-08-03 | Adicionado | `drf-spectacular`, `docs/api/openapi.md`, `config/urls.py` | OpenAPI/Swagger: `/api/schema/`, `/api/docs/`; endpoints `health`/`me` com `@extend_schema`; flag `DJANGO_ENABLE_API_DOCS`; rule `065`. | Documentação interativa da API; contratos no schema. |
| 2026-08-03 | Adicionado | `users/`, `organizations/`, `core/`, `api/v1/me/` | Fase 2: User (email), Organization, Membership, AuditLog, Admin com auditoria, `GET /me/` e `GET /me/organizations/`, `seed_demo`. | Fonte de verdade de identidade; JWT/RBAC nas fases seguintes. |
| 2026-08-03 | Removido | `setup/`, `api/v1/setup/` | App `setup` removido (não previsto no plano); health check movido para `api/v1/health/` sem app Django dedicado. | Menos app vazio; `GET /api/v1/health/` mantido. |
| 2026-08-03 | Adicionado | `Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml`, `config/settings/` | Fase 1: Compose (Django+Postgres+Redis), deps (`psycopg`, cors, redis), settings de banco/cache/CORS via env, CI (ruff+pytest) e `config.settings.test`. | Ambiente reproduzível; PR falha se lint/testes quebrarem. |
| 2026-08-03 | Documentado | `docs/adr/`, `docs/initial_plan/`, `README.md` | Fase 0: ADRs (IdP, tenant, JWT claims, sync), escopo/não-escopo, reconciliação do roadmap antigo e backlog macro (épicos 0–6). | Limites e decisões travadas versionados; próximo passo é Fase 1 (Docker/CI/Postgres). |
| 2026-08-03 | Adicionado | `config/`, `setup/`, `api/v1/`, `core/` | Projeto Django iniciado com settings por ambiente, app `setup` e health check em `/api/v1/health/`. | Base local executável para as próximas fases (usuários, org, JWT). |
| 2026-08-01 | Adicionado | `.cursor/` | Migradas rules e skills (Django + DRF) dos templates Arancia e FastAPI, adaptadas ao domínio multi-tenant. Índice em `docs/cursor/rules-index.md`. | Agente passa a seguir padrões de camadas, multi-tenancy, segurança e testes do projeto. |
| 2026-08-01 | Alterado | `.cursor/rules/` | Consolidadas rules herdadas: `000-django-global.mdc` removida (duplicada) e `000-django-rest-global.mdc` convertida em `docs/cursor/drf-reference.md`. | Contexto global mais enxuto, sem duplicação. |
| 2026-08-01 | Adicionado | `.cursor/` | Rule `007-feature-design-approval-always.mdc` (gate de aprovação de features) + skill `new-feature-design` (workflow specification-first em 13 fases). | Models, endpoints, telas e fluxos novos exigem especificação aprovada antes da implementação. |
| 2026-08-01 | Adicionado | `docs/design/` | Padrões de design da plataforma: identidade visual da marca (`identidade-visual.md`), design system do produto (`design-system.md`), tokens consolidados (`design-tokens.json`) e assets de logo/pranchas em `docs/design/assets/`. | Frontends e materiais da plataforma passam a ter fonte única de cores, tipografia, logos e componentes. |
| 2026-08-01 | Adicionado | `.cursor/` | Adaptados do awesome-cursorrules: rule `140-git-commits-always` (Conventional Commits), skill `revisar-pr` + stub `150-pr-review-manual`, rule `160-docker-auto` (globs Dockerfile/compose). | Commits padronizados; reviews de PR com ângulos multi-tenant; Docker só ativa quando houver Dockerfile. |
| 2026-08-03 | Alterado | `.cursor/rules/`, `docs/cursor/` | Rule `020` passa a exigir function-based views (`@api_view`); `060`, arquitetura, `drf-reference` e skills alinhados (sem ViewSet/router novos). | Agente cria endpoints como FBV + `path()`, não CBV/ViewSet. |

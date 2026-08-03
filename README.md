# organeasy-core
Core identity, authentication, tenancy and permissions service for the OrganEasy platform.

Responsável por:

Django;
Django REST Framework;
autenticação;
SimpleJWT;
usuários;
organizações;
permissões;
módulos habilitados;
auditoria;
Django Admin.

## Estrutura

```text
config/          # Projeto Django (settings por ambiente, urls, wsgi/asgi)
setup/           # App de fundação
api/v1/          # Endpoints versionados (FBV + path)
core/            # Abstrações compartilhadas
manage.py
```

## Setup local

```bash
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

Health check: `GET http://127.0.0.1:8000/api/v1/health/`

## Alterações recentes

| Data | Tipo | Módulo/Pasta | Alteração | Impacto |
| ---- | ---- | ------------ | --------- | ------- |
| 2026-08-03 | Adicionado | `config/`, `setup/`, `api/v1/`, `core/` | Projeto Django iniciado com settings por ambiente, app `setup` e health check em `/api/v1/health/`. | Base local executável para as próximas fases (usuários, org, JWT). |
| 2026-08-01 | Adicionado | `.cursor/` | Migradas rules e skills (Django + DRF) dos templates Arancia e FastAPI, adaptadas ao domínio multi-tenant. Índice em `docs/cursor/rules-index.md`. | Agente passa a seguir padrões de camadas, multi-tenancy, segurança e testes do projeto. |
| 2026-08-01 | Alterado | `.cursor/rules/` | Consolidadas rules herdadas: `000-django-global.mdc` removida (duplicada) e `000-django-rest-global.mdc` convertida em `docs/cursor/drf-reference.md`. | Contexto global mais enxuto, sem duplicação. |
| 2026-08-01 | Adicionado | `.cursor/` | Rule `007-feature-design-approval-always.mdc` (gate de aprovação de features) + skill `new-feature-design` (workflow specification-first em 13 fases). | Models, endpoints, telas e fluxos novos exigem especificação aprovada antes da implementação. |
| 2026-08-01 | Adicionado | `docs/design/` | Padrões de design da plataforma: identidade visual da marca (`identidade-visual.md`), design system do produto (`design-system.md`), tokens consolidados (`design-tokens.json`) e assets de logo/pranchas em `docs/design/assets/`. | Frontends e materiais da plataforma passam a ter fonte única de cores, tipografia, logos e componentes. |
| 2026-08-01 | Adicionado | `.cursor/` | Adaptados do awesome-cursorrules: rule `140-git-commits-always` (Conventional Commits), skill `revisar-pr` + stub `150-pr-review-manual`, rule `160-docker-auto` (globs Dockerfile/compose). | Commits padronizados; reviews de PR com ângulos multi-tenant; Docker só ativa quando houver Dockerfile. |
| 2026-08-03 | Alterado | `.cursor/rules/`, `docs/cursor/` | Rule `020` passa a exigir function-based views (`@api_view`); `060`, arquitetura, `drf-reference` e skills alinhados (sem ViewSet/router novos). | Agente cria endpoints como FBV + `path()`, não CBV/ViewSet. |

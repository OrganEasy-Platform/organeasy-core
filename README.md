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

## Alterações recentes

| Data | Tipo | Módulo/Pasta | Alteração | Impacto |
| ---- | ---- | ------------ | --------- | ------- |
| 2026-08-01 | Adicionado | `.cursor/` | Migradas rules e skills (Django + DRF) dos templates Arancia e FastAPI, adaptadas ao domínio multi-tenant. Índice em `docs/cursor/rules-index.md`. | Agente passa a seguir padrões de camadas, multi-tenancy, segurança e testes do projeto. |
| 2026-08-01 | Alterado | `.cursor/rules/` | Consolidadas rules herdadas: `000-django-global.mdc` removida (duplicada) e `000-django-rest-global.mdc` convertida em `docs/cursor/drf-reference.md`. | Contexto global mais enxuto, sem duplicação. |
| 2026-08-01 | Adicionado | `.cursor/` | Rule `007-feature-design-approval-always.mdc` (gate de aprovação de features) + skill `new-feature-design` (workflow specification-first em 13 fases). | Models, endpoints, telas e fluxos novos exigem especificação aprovada antes da implementação. |
| 2026-08-01 | Adicionado | `docs/design/` | Padrões de design da plataforma: identidade visual da marca (`identidade-visual.md`), design system do produto (`design-system.md`), tokens consolidados (`design-tokens.json`) e assets de logo/pranchas em `docs/design/assets/`. | Frontends e materiais da plataforma passam a ter fonte única de cores, tipografia, logos e componentes. |

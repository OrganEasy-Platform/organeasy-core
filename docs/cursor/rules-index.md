# Índice de Rules e Skills — organeasy-core

Documentação humana das rules ativas em `.cursor/rules/` e skills em `.cursor/skills/`.

## Rules

| Rule | Tipo | Finalidade |
| ---- | ---- | ---------- |
| `000-project-context-always.mdc` | always | Contexto do organeasy-core e fluxo recomendado. |
| `005-rule-vs-skill-gate-always.mdc` | always | Gate: Rule vs Skill vs docs antes de criar nova rule. |
| `007-feature-design-approval-always.mdc` | always | Gate: aprovação explícita antes de implementar models, endpoints, telas e fluxos → skill `new-feature-design`. |
| `010-django-architecture-always.mdc` | always | Responsabilidades por camada (models, views, serializers, services). |
| `015-python-style-auto.mdc` | auto | Estilo Python geral. |
| `020-django-views-drf-auto.mdc` | auto | Views DRF como FBV (`@api_view`); proíbe ViewSet/APIView novos. |
| `030-django-models-auto.mdc` | auto | Models e migrations. |
| `040-drf-serializers-auto.mdc` | auto | Serializers DRF. |
| `055-datetime-timezone-auto.mdc` | auto | UTC no banco, `timezone.now()`, `USE_TZ=True`. |
| `060-urls-routing-auto.mdc` | auto | URLs com `path()` + FBV; versionamento `/api/v1/`. |
| `070-services-utils-auto.mdc` | auto | Services e utils. |
| `075-github-actions-ci-auto.mdc` | auto (stub) | CI GitHub Actions → skill `configurar-ci-github-actions`. |
| `080-auth-multitenancy-always.mdc` | always | Autenticação, permissões e isolamento por organização. |
| `090-tests-auto.mdc` | auto | Testes Django/DRF. |
| `100-security-settings-always.mdc` | always | Segurança, settings, secrets. |
| `110-docs-readme-auto.mdc` | auto | README e documentação. |
| `115-reusable-core-abstractions-auto.mdc` | auto | Avaliar `core/` antes de criar classes reutilizáveis. |
| `120-business-rules-discovery-manual.mdc` | manual (stub) | Descoberta de regras de negócio → skill `descobrir-regras-negocio`. |
| `130-task-workflow-agent.mdc` | manual (stub) | Tarefas multi-camada → skill `executar-tarefa-django-drf`. |
| `140-git-commits-always.mdc` | always | Conventional Commits para mensagens de commit. |
| `150-pr-review-manual.mdc` | manual (stub) | Review de PR/diff → skill `revisar-pr`. |
| `160-docker-auto.mdc` | auto | Dockerfile e docker-compose (Python/Django). |

## Regras de negócio específicas

Novas regras confirmadas devem ser criadas como:

```text
.cursor/rules/2xx-business-<dominio>-auto.mdc
```

Exemplos: `200-business-organizations-auto.mdc`, `210-business-modules-auto.mdc`.

A pasta `.cursor/business-rules/` registra descobertas, perguntas e decisões antes de virarem rule ativa.

## Documentação de referência

| Doc | Conteúdo |
| --- | -------- |
| `docs/cursor/drf-reference.md` | Estrutura de pastas (apps, `api/v1/`, `core/`, `config/settings/`), formato unificado de erro e padrões DRF detalhados. |

## Skills

| Skill | Uso |
| ----- | --- |
| `executar-tarefa-django-drf` | Tarefas multi-camada. |
| `new-feature-design` | Especificação e aprovação de features (specification-first). |
| `descobrir-regras-negocio` | Mapear negócio → rules 2xx. |
| `configurar-ci-github-actions` | Pipeline CI de testes unitários. |
| `auditar-rules-skills-docs` | Auditoria de rules, skills e docs. |
| `revisar-pr` | Review de PR/diff (segurança, performance, testes, arquitetura). |

## Origem

Migrado e adaptado de `Arancia_CursorRules_Django` (rules Django) e `TemplateFastAPI_cursor_rules` (skills e rules agnósticas), com adaptações para Django + DRF e para o domínio multi-tenant do OrganEasy.

Itens adicionais adaptados de `awesome-cursorrules` (2026-08-01): Conventional Commits (`140`), skill `revisar-pr` + stub (`150`), Docker (`160`).

As rules herdadas do setup inicial (`000-django-global.mdc` e `000-django-rest-global.mdc`) foram consolidadas em 2026-08-01: a primeira era duplicação das rules migradas e foi removida; a segunda virou `docs/cursor/drf-reference.md`.

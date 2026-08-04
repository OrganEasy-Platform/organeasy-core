# Reconciliação: roadmap estratégico antigo × plano revisado

**Data:** 2026-08-03  
**Status:** Nota normativa para este repositório

## Problema

O arquivo [OrganEasy_Roadmap_Estrategico.md](OrganEasy_Roadmap_Estrategico.md) descreve a visão de alto nível do OrganEasy, mas a **stack do núcleo** nele está desatualizada: aponta FastAPI + SQLAlchemy + Alembic como base da plataforma, com autenticação/JWT como etapa genérica sem Django como IdP.

O documento mestre vigente é [OrganEasy_Plano_de_Implementacao_Revisado.md](OrganEasy_Plano_de_Implementacao_Revisado.md) (julho/2026).

## O que permanece válido no roadmap antigo

- Visão: SaaS multi-tenant modular com padrões de produção
- Objetivos de portfólio: arquitetura, Docker, observabilidade, testes, CI/CD, domínio empresarial
- Temas de produto posteriores: Kanban, Chat, Financeiro, RH, WMS, TMS, E-commerce
- Práticas: commits pequenos, releases por fase, Issues/Projects, documentação

## O que muda (obrigatório neste repo)

| Tema | Roadmap antigo | Plano revisado / `organeasy-core` |
| ---- | -------------- | --------------------------------- |
| Núcleo de identidade | Implícito / FastAPI | **Django + DRF + SimpleJWT** ([ADR 0001](../adr/0001-django-as-idp.md)) |
| Stack FastAPI | “A” plataforma | **Módulos de negócio** fora do core (outro serviço/repo até existir monorepo) |
| Auth | Etapa genérica “JWT, refresh, usuários” | Emitido no Django; módulos **validam** o token |
| Multi-tenancy | Organizações / isolamento | Coluna `organization_id` + `org_id` no JWT ([ADR 0002](../adr/0002-multi-tenancy-by-column.md)) |
| Ordem de entrega | Fundação → infra Swarm cedo | Fases **0–6 do core** antes de módulos; Swarm/HAProxy/observabilidade completa depois |
| Monorepo | Não detalhado aqui | Desejável no plano revisado; **hoje** o escopo versionado é só `organeasy-core` |

## Como ler os dois documentos

```text
OrganEasy_Roadmap_Estrategico.md     → visão ampla e lista de módulos (histórico)
OrganEasy_Plano_de_Implementacao_Revisado.md → documento mestre (stack + fases)
docs/initial_plan/escopo-e-nao-escopo.md     → limites deste repositório
docs/adr/                                    → decisões travadas
```

Em caso de conflito de stack ou responsabilidades do IdP, **prevalece o plano revisado + ADRs**.

## Impacto para implementadores e agentes

1. Não iniciar IdP em FastAPI neste repositório.
2. Não tratar módulos ERP como entregáveis do `organeasy-core` nas Fases 0–6.
3. Citar o plano revisado e os ADRs ao abrir trabalho de feature (rule `007`).

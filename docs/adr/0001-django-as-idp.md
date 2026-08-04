# ADR 0001 — Django como Identity Provider (IdP)

- **Status:** Aceito
- **Data:** 2026-08-03
- **Contexto:** Fase 0 — definição e limites (`organeasy-core`)

## Contexto

A plataforma OrganEasy precisa de identidade centralizada: usuários, organizações, autenticação, papéis, administração e catálogo de módulos. Módulos de negócio (Kanban, Financeiro, etc.) devem consumir tokens emitidos por um único provedor, sem reimplementar login em cada serviço.

Há experiência prática prévia com Django como núcleo de identidade em produção. Um segundo mecanismo de autenticação “só para o portfólio” aumentaria custo e risco sem benefício claro nesta etapa.

## Decisão

O **Django + Django REST Framework + SimpleJWT** é o Identity Provider da plataforma neste repositório (`organeasy-core`).

Responsabilidades do core:

- Cadastro, ativação, bloqueio e recuperação de usuários
- Organizações e vínculo usuário–organização
- Emissão, renovação e revogação de JWT
- RBAC e catálogo de módulos habilitados por organização
- Django Admin e auditoria administrativa
- Endpoints de identidade (perfil, orgs disponíveis, troca de contexto)

Módulos FastAPI (fora deste repo, por enquanto) **validam** o JWT emitido pelo Django; não autenticam o usuário do zero.

## Alternativas consideradas

| Alternativa | Motivo de rejeição (agora) |
| ----------- | -------------------------- |
| FastAPI + SQLAlchemy como IdP | Duplicaria o que o Django Admin e o ecossistema de auth já resolvem; diverge da experiência operacional existente |
| Auth externo (Keycloak/Auth0) | Overhead operacional e menos evidência de implementação própria no portfólio inicial |
| Auth espalhada por módulo | Multiplica superfície de ataque e inconsistência de claims |

## Consequências

- Este repositório é o serviço de identidade; módulos de negócio não vivem aqui na Fase 0–6.
- Claims e contratos JWT devem ser versionados e estáveis para consumidores futuros.
- Stack FastAPI no roadmap antigo aplica-se a **módulos**, não ao núcleo de identidade — ver [roadmap-reconciliation.md](../initial_plan/roadmap-reconciliation.md).

# Backlog macro — organeasy-core (Fases 0–6)

Épicos ordenados para o serviço de identidade. Dependências são sequenciais: um épico só inicia com o anterior demonstrável (e com especificação aprovada quando houver models/contratos — rule `007`).

**Fontes:** plano revisado §8/§13 · [escopo-e-nao-escopo.md](escopo-e-nao-escopo.md) · [ADRs](../adr/README.md).

> Issues criadas em 2026-08-03 no GitHub (`OrganEasy-Platform/organeasy-core`). Este arquivo permanece a fonte versionada do backlog.

## Visão da sequência

```text
User/Org → JWT → tenant → RBAC → módulos
   (2)      (3)    (4)     (5)      (6)
```

Fases 0–1 são fundação (docs + infra) e não entregam domínio de produto.

---

## Épico E0 — Definição e limites

| Campo | Valor |
| ----- | ----- |
| Fase | 0 |
| Status | Concluído (docs) |
| Objetivo | Visão executável, ADRs, escopo/não-escopo, backlog |
| Entregáveis | README, `docs/adr/*`, escopo, reconciliação do roadmap, este backlog |
| Dependências | — |
| Riscos | Escopo “ERP infinito”; docs desatualizados vs plano revisado |

---

## Épico E1 — Fundação técnica

| Campo | Valor |
| ----- | ----- |
| Fase | 1 |
| Status | Implementado no repo — Issue [#19](https://github.com/OrganEasy-Platform/organeasy-core/issues/19) |
| Objetivo | Ambiente reproduzível e pipeline mínimo |
| Entregáveis | `docker-compose` (Django + PostgreSQL + Redis), Dockerfile, CI GitHub Actions, deps (`psycopg`, cors, redis), README de compose |
| Dependências | E0 |
| Riscos | Segredos versionados; CI flaky; desvio de settings por ambiente |
| Critério de pronto | README sobe o ambiente; PR falha se testes falharem |

---

## Épico E2 — Identidade (User / Organization)

| Campo | Valor |
| ----- | ----- |
| Fase | 2 |
| Status | Concluída (spec aprovada + implementação) |
| Objetivo | Fonte de verdade de usuários e organizações |
| Entregáveis | Apps `users` / `organizations`; Admin; API mínima perfil + orgs do usuário; auditoria administrativa (`core.AuditLog`) |
| Dependências | E1 |
| Riscos | Modelagem prematura; vazamento cross-org na listagem; User custom vs extensão mal definida |
| Critério de pronto | Admin cria org/user/vínculo; usuário só vê suas orgs; testes de model/regra |
| Doc | [modelo-identidade.md](../identity/modelo-identidade.md) |

---

## Épico E3 — Autenticação JWT (SimpleJWT)

| Campo | Valor |
| ----- | ----- |
| Fase | 3 |
| Status | Pendente — especificação antes dos endpoints |
| Objetivo | Emitir tokens no Django (IdP) |
| Entregáveis | FBV: login, refresh, logout, me; rotação + blacklist; claims do [ADR 0003](../adr/0003-jwt-minimal-claims.md); formato de erro unificado; testes de expirado/inválido/revogado |
| Dependências | E2 |
| Riscos | Claims instáveis para consumidores futuros; log de token completo; HS256 em prod sem plano RS256 |
| Critério de pronto | login → access → me; logout invalida refresh; contrato JWT documentado |

---

## Épico E4 — Multi-tenancy no core

| Campo | Valor |
| ----- | ----- |
| Fase | 4 |
| Status | Pendente — especificação antes dos endpoints de contexto |
| Objetivo | Organização ativa e isolamento |
| Entregáveis | Org ativa no login e/ou troca de contexto; `org_id` no JWT; helpers de tenant em services; testes negativos cross-tenant |
| Dependências | E3 |
| Riscos | Aceitar `organization_id` do body como verdade; consultas sem tenant “passando” |
| Critério de pronto | Sem contexto de tenant, falha segura; suíte de isolamento verde |

---

## Épico E5 — RBAC

| Campo | Valor |
| ----- | ----- |
| Fase | 5 |
| Status | Pendente — especificação antes de models de papel |
| Objetivo | Papéis/escopos por organização, consumíveis pelo token |
| Entregáveis | Papéis padrão + custom; map permissão → scope `modulo:acao`; scopes no JWT; Admin; auditoria de concessão; testes 401 vs 403 |
| Dependências | E4 |
| Riscos | Token inflado; nomenclatura inconsistente; confundir Group global com papel da org |
| Critério de pronto | Sem permissão → 403; scopes consistentes |

---

## Épico E6 — Catálogo de módulos

| Campo | Valor |
| ----- | ----- |
| Fase | 6 |
| Status | Pendente — especificação antes de models |
| Objetivo | Feature flags / módulos habilitados por organização |
| Entregáveis | Models módulo + habilitação + dependências; endpoint de capacidades; bloqueio sem apagar dados; testes ativar/desativar |
| Dependências | E5 |
| Riscos | Dependências cíclicas entre módulos; desabilitar sem UX clara para o cliente |
| Critério de pronto | Capacidades só via backend; módulo off bloqueia acesso |

---

## Explicitamente fora deste backlog (não criar épicos aqui)

- Kanban, Chat, Financeiro, RH, WMS, TMS, E-commerce
- Swarm / HAProxy / Grafana-Prometheus-Loki-Tempo completos
- Frontend de produto (além do Django Admin)

## Issues no GitHub

| Épico | Issue | Labels | Estado |
| ----- | ----- | ------ | ------ |
| E0 | [#18](https://github.com/OrganEasy-Platform/organeasy-core/issues/18) `docs(core): Fase 0 — ADRs e escopo` | `epic`, `phase-0` | Fechada |
| E1 | [#19](https://github.com/OrganEasy-Platform/organeasy-core/issues/19) `chore(ci): Fase 1 — Docker Compose, Postgres e GitHub Actions` | `epic`, `phase-1` | Fechada |
| E2 | [#20](https://github.com/OrganEasy-Platform/organeasy-core/issues/20) `feat(users): Fase 2 — User, Organization e vínculo` | `epic`, `phase-2` | Fechada |
| E3 | [#21](https://github.com/OrganEasy-Platform/organeasy-core/issues/21) `feat(auth): Fase 3 — SimpleJWT login/refresh/logout/me` | `epic`, `phase-3`, `needs-spec` | Aberta |
| E4 | [#22](https://github.com/OrganEasy-Platform/organeasy-core/issues/22) `feat(organizations): Fase 4 — contexto de tenant e org_id no JWT` | `epic`, `phase-4`, `needs-spec` | Aberta |
| E5 | [#23](https://github.com/OrganEasy-Platform/organeasy-core/issues/23) `feat(auth): Fase 5 — RBAC e scopes por organização` | `epic`, `phase-5`, `needs-spec` | Aberta |
| E6 | [#24](https://github.com/OrganEasy-Platform/organeasy-core/issues/24) `feat(organizations): Fase 6 — catálogo de módulos habilitáveis` | `epic`, `phase-6`, `needs-spec` | Aberta |

Labels: `phase-0` … `phase-6`, `epic`, `needs-spec` (Fases 3–6).

# ADR 0003 — Claims JWT mínimas

- **Status:** Aceito
- **Data:** 2026-08-03
- **Contexto:** Fase 0 — definição e limites (`organeasy-core`)

## Contexto

Módulos FastAPI e clientes precisam autorizar e isolar dados sem consultar o IdP a cada request. O token deve carregar o mínimo necessário para autenticação, tenant e autorização de alto nível, sem inflar o JWT com catálogos grandes de permissões.

## Decisão

Access tokens emitidos pelo SimpleJWT (Django) devem incluir, no mínimo:

| Claim | Exemplo | Finalidade |
| ----- | ------- | ---------- |
| `sub` | ID imutável do usuário | Identificação do principal |
| `org_id` | ID da organização ativa | Isolamento multi-tenant |
| `roles` | `["admin", "manager"]` | Autorização de alto nível |
| `scopes` | `["kanban:read", "kanban:write"]` | Permissões consumíveis pelos módulos (`modulo:acao`) |
| `iss` | `organeasy-auth` | Validação do emissor |
| `aud` | `organeasy-services` | Restringir consumidores |
| `jti` | UUID | Revogação e auditoria |
| `exp` / `iat` | timestamps | Expiração e rastreabilidade |

Políticas complementares:

- Access token curto; refresh com rotação e blacklist.
- Protótipo local: HS256 aceitável; ambientes publicados devem evoluir para RS256/JWKS.
- Não colocar volume grande de permissões no token; preferir scopes relevantes ao contexto.
- Nunca versionar segredos de assinatura no repositório.

Valores literais de `iss`/`aud` fixados na Fase 3: `organeasy-auth` / `organeasy-services` (override via `JWT_ISSUER` / `JWT_AUDIENCE`). Scopes iniciais: lista vazia até a Fase 5 (RBAC). Ver [jwt-contract.md](../identity/jwt-contract.md).

## Alternativas consideradas

| Alternativa | Motivo de rejeição (agora) |
| ----------- | -------------------------- |
| Token só com `sub` + lookup no IdP a cada request | Aumenta acoplamento e latência; piora disponibilidade dos módulos |
| Embedar árvore completa de permissões | Token pesado e desatualizado até expirar |
| Session cookie apenas (sem JWT) | Adequado ao Admin; insuficiente para APIs de módulos distribuídos |

## Consequências

- Contrato JWT documentado para consumidores FastAPI futuros, mesmo antes deles existirem neste monorepo.
- Mudanças em claims são breaking para consumidores — versionar e comunicar.
- RBAC (Fase 5) alimenta `roles`/`scopes`; tenant (Fase 4) alimenta `org_id`.

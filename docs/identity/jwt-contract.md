# Contrato JWT — organeasy-core (Fases 3–4)

Documento para consumidores (frontend e módulos FastAPI futuros). Alinhado ao [ADR 0003](../adr/0003-jwt-minimal-claims.md).

## Fluxo

```text
Cliente → POST /api/v1/auth/login/ (email + password [+ organization_id?])
       ← access + refresh  (org_id resolvido: explicit → default → única → null)
Cliente → GET /api/v1/me/  Authorization: Bearer <access>
       ← perfil + active_organization (do claim org_id)
Cliente → POST /api/v1/auth/switch-organization/  Bearer + { organization_id [, refresh] }
       ← nova pair com org_id alvo (refresh antigo blacklisted se enviado)
Cliente → POST /api/v1/auth/refresh/  { refresh }
       ← access + refresh (preserva org_id; revalida membership)
Cliente → POST /api/v1/auth/logout/  Bearer + { refresh }
       ← 200; refresh revogado
```

## Endpoints

| Método | Rota | Auth | Corpo |
| ------ | ---- | ---- | ----- |
| `POST` | `/api/v1/auth/login/` | público | `{ "email", "password", "organization_id"? }` |
| `POST` | `/api/v1/auth/refresh/` | público | `{ "refresh" }` |
| `POST` | `/api/v1/auth/logout/` | Bearer access | `{ "refresh" }` |
| `POST` | `/api/v1/auth/switch-organization/` | Bearer access | `{ "organization_id", "refresh"? }` |
| `GET` | `/api/v1/me/` | Bearer ou Session | — |
| `GET` | `/api/v1/me/organizations/` | Bearer ou Session | — |

Respostas de sucesso usam o envelope `{ "success": true, "data": ... }` (logout: `message`, sem `data` obrigatório). Erros: formato unificado (`error_code`, etc.).

### Login / refresh / switch `data`

```json
{
  "access": "<jwt>",
  "refresh": "<jwt>",
  "token_type": "Bearer",
  "expires_in": 900
}
```

`expires_in` = lifetime do **access** em segundos.

### Resolução de `org_id` no login

1. `organization_id` no body → valida membership `active` + org `active` (senão **403** `ORGANIZATION_NOT_ALLOWED`)
2. Senão membership com `is_default=True` (ativos)
3. Senão exatamente **1** org disponível → usa essa
4. Senão → `org_id=null` (Pacote A; onboarding de criar/entrar org = Pacote B futuro)

### Refresh e membership

- Preserva `org_id` do refresh e revalida o vínculo.
- Se o membership/org não for mais válido → **403** `ORGANIZATION_MEMBERSHIP_LOST` (novo login ou switch).

### `/me` — `active_organization`

```json
{
  "id": "...",
  "email": "...",
  "full_name": "...",
  "status": "active",
  "active_organization": { "id": "...", "name": "...", "slug": "..." }
}
```

`active_organization` é `null` se o access não tiver `org_id`, se a Session não trouxer claim, ou se o vínculo não for mais válido. Fonte: claim do Bearer (não o body).

## Claims do access token

| Claim | Fase 4 | Notas |
| ----- | ------ | ----- |
| `sub` | UUID do usuário (string) | Identificador imutável |
| `org_id` | UUID string ou `null` | Organização ativa |
| `roles` | `[]` | RBAC na Fase 5 |
| `scopes` | `[]` | RBAC na Fase 5 |
| `iss` | `organeasy-auth` | Override: `JWT_ISSUER` |
| `aud` | `organeasy-services` | Override: `JWT_AUDIENCE` |
| `jti` | UUID | Revogação / auditoria |
| `exp` / `iat` | timestamps | Expiração |
| `token_type` | `access` | SimpleJWT |

O **refresh** também carrega `org_id` (mesma regra) para preservar contexto na rotação.

## Assinatura

| Ambiente | Algoritmo | Chave |
| -------- | --------- | ----- |
| Local / CI (agora) | HS256 | `JWT_SIGNING_KEY` ou `DJANGO_SECRET_KEY` |
| Publicado (futuro) | RS256 + JWKS | Fora do escopo atual |

## Lifetimes (defaults)

| Token | Env | Default |
| ----- | --- | ------- |
| Access | `JWT_ACCESS_LIFETIME_SECONDS` | `900` (15 min) |
| Refresh | `JWT_REFRESH_LIFETIME_SECONDS` | `604800` (7 dias) |

Rotação de refresh + blacklist após rotação, no logout e no switch (quando `refresh` é enviado).

## Validação esperada no consumidor (FastAPI futuro)

1. Assinatura (HS256 local / JWKS depois)
2. `exp`, `iss`, `aud`
3. Extrair `sub` e `org_id` (tratar `null` como “sem tenant”)
4. Endpoints de tenant: falhar se `org_id` ausente
5. **Não** aceitar `organization_id` do body como fonte de verdade do tenant

## Segurança / logs

- Nunca logar access/refresh completos.
- Access expirado ou inválido → 401 antes da regra de negócio.
- Org inválida no login/switch → 403 `ORGANIZATION_NOT_ALLOWED` (sem enumerar existência).
- Troca de contexto gera `AuditLog` (`switch_context`).
- Superuser/staff de plataforma pode ter `org_id=null`; obrigação de org para usuários de produto completa-se no Pacote B (onboarding).

## OpenAPI

Contratos anotados em `/api/docs/` (tag `auth` / `me`).

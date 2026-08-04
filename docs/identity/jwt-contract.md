# Contrato JWT — organeasy-core (Fase 3)

Documento para consumidores (frontend e módulos FastAPI futuros). Alinhado ao [ADR 0003](../adr/0003-jwt-minimal-claims.md).

## Fluxo

```text
Cliente → POST /api/v1/auth/login/ (email + password)
       ← access + refresh
Cliente → GET /api/v1/me/  Authorization: Bearer <access>
Cliente → POST /api/v1/auth/refresh/  { refresh }
       ← access + refresh (rotação; refresh anterior na blacklist)
Cliente → POST /api/v1/auth/logout/  Bearer + { refresh }
       ← 200; refresh revogado
```

## Endpoints

| Método | Rota | Auth | Corpo |
| ------ | ---- | ---- | ----- |
| `POST` | `/api/v1/auth/login/` | público | `{ "email", "password" }` |
| `POST` | `/api/v1/auth/refresh/` | público | `{ "refresh" }` |
| `POST` | `/api/v1/auth/logout/` | Bearer access | `{ "refresh" }` |
| `GET` | `/api/v1/me/` | Bearer ou Session | — |
| `GET` | `/api/v1/me/organizations/` | Bearer ou Session | — |

Respostas de sucesso usam o envelope `{ "success": true, "data": ... }` (logout: `message`, sem `data` obrigatório). Erros: formato unificado (`error_code`, etc.).

### Login / refresh `data`

```json
{
  "access": "<jwt>",
  "refresh": "<jwt>",
  "token_type": "Bearer",
  "expires_in": 900
}
```

`expires_in` = lifetime do **access** em segundos.

## Claims do access token

| Claim | Fase 3 | Notas |
| ----- | ------ | ----- |
| `sub` | UUID do usuário (string) | Identificador imutável |
| `org_id` | `null` | Organização ativa na Fase 4 |
| `roles` | `[]` | RBAC na Fase 5 |
| `scopes` | `[]` | RBAC na Fase 5 |
| `iss` | `organeasy-auth` | Override: `JWT_ISSUER` |
| `aud` | `organeasy-services` | Override: `JWT_AUDIENCE` |
| `jti` | UUID | Revogação / auditoria |
| `exp` / `iat` | timestamps | Expiração |
| `token_type` | `access` | SimpleJWT |

## Assinatura

| Ambiente | Algoritmo | Chave |
| -------- | --------- | ----- |
| Local / CI (agora) | HS256 | `JWT_SIGNING_KEY` ou `DJANGO_SECRET_KEY` |
| Publicado (futuro) | RS256 + JWKS | Fora do escopo da Fase 3 |

## Lifetimes (defaults)

| Token | Env | Default |
| ----- | --- | ------- |
| Access | `JWT_ACCESS_LIFETIME_SECONDS` | `900` (15 min) |
| Refresh | `JWT_REFRESH_LIFETIME_SECONDS` | `604800` (7 dias) |

Rotação de refresh + blacklist após rotação e no logout.

## Validação esperada no consumidor (FastAPI futuro)

1. Assinatura (HS256 local / JWKS depois)
2. `exp`, `iss`, `aud`
3. Extrair `sub`; tratar `org_id`/`roles`/`scopes` quando preenchidos
4. **Não** aceitar `organization_id` do body como fonte de verdade do tenant

## Segurança / logs

- Nunca logar access/refresh completos.
- Access expirado ou inválido → 401 antes da regra de negócio.
- Refresh revogado (logout ou rotação) não renova.

## OpenAPI

Contratos anotados em `/api/docs/` (tag `auth`).

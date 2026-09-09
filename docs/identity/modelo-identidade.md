# Modelo de identidade — organeasy-core (Fases 2–4 + Pacote B)

Fonte de verdade de usuários e organizações no IdP Django; emissão JWT via SimpleJWT com organização ativa (Fase 4); onboarding self-service (Pacote B).

## Entidades

| Entidade | App | Responsabilidade |
| -------- | --- | ---------------- |
| `User` | `users` | Conta de identidade (email + status active/blocked) |
| `Organization` | `organizations` | Tenant lógico (`created_by` para limite de criação) |
| `OrganizationMembership` | `organizations` | Vínculo User↔Organization (`status`, `is_default`) |
| `OrganizationInviteCode` | `organizations` | Código de convite (Pacote B) |
| `OrganizationJoinRequest` | `organizations` | Pedido de entrada + aprovação (Pacote B) |
| `AuditLog` | `core` | Auditoria administrativa, switch e onboarding |
| Outstanding/Blacklisted token | SimpleJWT | Refresh outstanding + blacklist |

## Regras

- Login identifier: `email` (`USERNAME_FIELD`).
- Usuário `blocked` → `is_active=False` (não autentica).
- Listagem de orgs do usuário: só membership `active` + org `active`.
- Nunca aceitar `organization_id` do client como fonte de verdade do tenant sem validar o vínculo.
- Resolução de org no login: explicit → `is_default` → única org → `null`.
- Troca de contexto: `POST /api/v1/auth/switch-organization/` (nova pair; AuditLog).
- Refresh preserva `org_id` e revalida membership (senão 403).
- API autenticada: JWT Bearer (preferencial) e Session (Admin/dev).
- Onboarding: [onboarding.md](onboarding.md) (criar org, código, pedido).
- Papéis/scopes reais: Fase 5.

## API

| Método | Rota | Auth |
| ------ | ---- | ---- |
| `POST` | `/api/v1/auth/login/` | público |
| `POST` | `/api/v1/auth/refresh/` | público |
| `POST` | `/api/v1/auth/logout/` | JWT |
| `POST` | `/api/v1/auth/switch-organization/` | JWT |
| `GET` | `/api/v1/me/` | JWT ou Session |
| `GET` | `/api/v1/me/organizations/` | JWT ou Session |
| `POST` | `/api/v1/organizations/` | JWT |
| `POST` | `/api/v1/organizations/join-by-code/` | JWT |
| `GET`/`POST` | `/api/v1/organizations/{id}/join-requests/` | JWT |
| `POST` | `/api/v1/organizations/{id}/join-requests/{rid}/approve\|reject/` | JWT + membro |
| `POST` | `/api/v1/organizations/join-requests/{rid}/cancel/` | JWT |
| `GET`/`POST` | `/api/v1/organizations/{id}/invite-codes/` | JWT + membro |
| `POST` | `/api/v1/organizations/{id}/invite-codes/{cid}/deactivate/` | JWT + membro |

Contrato JWT: [jwt-contract.md](jwt-contract.md). Onboarding: [onboarding.md](onboarding.md).

## Seed local

```bash
python manage.py seed_demo
```

Cria `admin@organeasy.local` / `membro@organeasy.local` (senhas só para demo local).

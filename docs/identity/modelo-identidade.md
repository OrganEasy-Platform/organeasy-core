# Modelo de identidade — organeasy-core (Fases 2–4)

Fonte de verdade de usuários e organizações no IdP Django; emissão JWT via SimpleJWT com organização ativa (Fase 4).

## Entidades

| Entidade | App | Responsabilidade |
| -------- | --- | ---------------- |
| `User` | `users` | Conta de identidade (email + status active/blocked) |
| `Organization` | `organizations` | Tenant lógico |
| `OrganizationMembership` | `organizations` | Vínculo User↔Organization (`status`, `is_default`) |
| `AuditLog` | `core` | Auditoria administrativa + troca de contexto |
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
- Papéis/scopes reais: Fase 5.
- Onboarding (criar org / entrar com código ou aprovação): Pacote B (após Fase 4).

## API

| Método | Rota | Auth |
| ------ | ---- | ---- |
| `POST` | `/api/v1/auth/login/` | público |
| `POST` | `/api/v1/auth/refresh/` | público |
| `POST` | `/api/v1/auth/logout/` | JWT |
| `POST` | `/api/v1/auth/switch-organization/` | JWT |
| `GET` | `/api/v1/me/` | JWT ou Session |
| `GET` | `/api/v1/me/organizations/` | JWT ou Session |

CRUD de user/org/vínculo: Django Admin (criação/entrada self-service = Pacote B).

Contrato JWT (claims, lifetimes, validação): [jwt-contract.md](jwt-contract.md).

## Seed local

```bash
python manage.py seed_demo
```

Cria `admin@organeasy.local` / `membro@organeasy.local` (senhas só para demo local).

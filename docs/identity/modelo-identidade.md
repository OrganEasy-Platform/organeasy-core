# Modelo de identidade — organeasy-core (Fase 2)

Fonte de verdade de usuários e organizações no IdP Django.

## Entidades

| Entidade | App | Responsabilidade |
| -------- | --- | ---------------- |
| `User` | `users` | Conta de identidade (email + status active/blocked) |
| `Organization` | `organizations` | Tenant lógico |
| `OrganizationMembership` | `organizations` | Vínculo User↔Organization (`status`, `is_default`) |
| `AuditLog` | `core` | Auditoria administrativa (create/update/status_change) |

## Regras

- Login identifier: `email` (`USERNAME_FIELD`).
- Usuário `blocked` → `is_active=False` (não autentica).
- Listagem de orgs do usuário: só membership `active` + org `active`.
- Nunca aceitar `organization_id` do client como fonte de verdade do vínculo.
- Papéis/scopes: Fase 5. Org ativa no JWT: Fase 4. JWT: Fase 3.

## API (Fase 2)

| Método | Rota | Auth |
| ------ | ---- | ---- |
| `GET` | `/api/v1/me/` | Session (`IsAuthenticated`) |
| `GET` | `/api/v1/me/organizations/` | Session (`IsAuthenticated`) |

CRUD de user/org/vínculo: Django Admin.

## Seed local

```bash
python manage.py seed_demo
```

Cria `admin@organeasy.local` / `membro@organeasy.local` (senhas só para demo local).

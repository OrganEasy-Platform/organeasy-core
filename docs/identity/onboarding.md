# Onboarding de organizações — Pacote B

Self-service para criar organização e entrar em organizações existentes. Depende da Fase 4 (tenant / `org_id` no JWT).

## Regras

- Criar organização: limite `ORG_CREATE_LIMIT` (default **1**) por `created_by`; orgs sem `created_by` (Admin/legado) **não** contam.
- Pertencer a N organizações é livre.
- Entrar: **código de convite** ou **pedido + aprovação** (qualquer membro `active` da org; hierarquia na Fase 5).
- Create e join-by-code devolvem **nova pair JWT** com `org_id`.
- Approve **não** emite tokens do solicitante.
- Evolução: pagamento para criar >1 org (só alterar o limite / política).

## API

| Método | Rota | Auth |
| ------ | ---- | ---- |
| `POST` | `/api/v1/organizations/` | JWT |
| `POST` | `/api/v1/organizations/join-by-code/` | JWT |
| `GET`/`POST` | `/api/v1/organizations/{id}/join-requests/` | JWT (POST qualquer auth; GET membro) |
| `POST` | `/api/v1/organizations/{id}/join-requests/{rid}/approve/` | JWT + membro |
| `POST` | `/api/v1/organizations/{id}/join-requests/{rid}/reject/` | JWT + membro |
| `POST` | `/api/v1/organizations/join-requests/{rid}/cancel/` | JWT (solicitante) |
| `GET`/`POST` | `/api/v1/organizations/{id}/invite-codes/` | JWT + membro |
| `POST` | `/api/v1/organizations/{id}/invite-codes/{cid}/deactivate/` | JWT + membro |

## Models

- `Organization.created_by`
- `OrganizationInviteCode`
- `OrganizationJoinRequest` (`pending` / `approved` / `rejected` / `cancelled`)

Ver também [modelo-identidade.md](modelo-identidade.md) e [jwt-contract.md](jwt-contract.md).

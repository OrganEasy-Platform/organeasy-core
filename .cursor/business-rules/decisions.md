# Decisões Confirmadas

Use este arquivo para registrar decisões de negócio confirmadas pelo usuário ou time.

| Data | Módulo | Decisão | Impacto |
| ---- | ------ | ------- | ------- |
| 2026-08-03 | identity | Fase 2 aprovada: User custom (email), Organization, Membership (`status`+`is_default`), AuditLog em `core`, API `GET /me/` e `GET /me/organizations/` (Session), Admin com auditoria | Apps `users`/`organizations`/`core`; JWT/RBAC ficam nas Fases 3–5 |
| 2026-08-03 | auth | Fase 3 aprovada: SimpleJWT FBV login/refresh/logout; `org_id=null` até Fase 4; roles/scopes `[]`; iss/aud do ADR; logout 200; access 15m / refresh 7d; HS256; rotação+blacklist | Endpoints `/api/v1/auth/*`; JWT em `/me`; contrato em `docs/identity/jwt-contract.md` |

# Decisões Confirmadas

Use este arquivo para registrar decisões de negócio confirmadas pelo usuário ou time.

| Data | Módulo | Decisão | Impacto |
| ---- | ------ | ------- | ------- |
| 2026-08-17 | tenant | Fase 4 (Pacote A) aprovada: org ativa no JWT; login com `organization_id` opcional (explicit→default→única→null); switch com nova pair + blacklist opcional do refresh; refresh preserva/revalida `org_id` (membership perdido→403); `/me.active_organization`; AuditLog `switch_context`; superuser pode `org_id=null`; login sem org permitido até Pacote B | Endpoints auth/me; `organizations.services.tenant_service`; docs JWT |
| 2026-08-17 | onboarding | Pacote B (após Fase 4): criar organização pela API com limite inicial de **1 org criada por usuário**; pertencer a N orgs; entrar por **código** e por **pedido+aprovação**; evolução comercial futura (pagamento para criar >1 org) | Spec futura; sem implementação nesta leva |
| 2026-08-17 | modules | Fase 6 + frontend: home com catálogo de módulos; itens não habilitados/sem MVP como `coming_soon` / “em breve” | Fora da Fase 4; depende E5/E6 |
| 2026-08-03 | identity | Fase 2 aprovada: User custom (email), Organization, Membership (`status`+`is_default`), AuditLog em `core`, API `GET /me/` e `GET /me/organizations/` (Session), Admin com auditoria | Apps `users`/`organizations`/`core`; JWT/RBAC ficam nas Fases 3–5 |
| 2026-08-03 | auth | Fase 3 aprovada: SimpleJWT FBV login/refresh/logout; `org_id=null` até Fase 4; roles/scopes `[]`; iss/aud do ADR; logout 200; access 15m / refresh 7d; HS256; rotação+blacklist | Endpoints `/api/v1/auth/*`; JWT em `/me`; contrato em `docs/identity/jwt-contract.md` |

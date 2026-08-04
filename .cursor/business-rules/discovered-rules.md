# Regras de Negócio Descobertas

Use este arquivo para registrar regras encontradas durante análise do projeto.

## Confirmadas pelo código

- Listagem de organizações do usuário só inclui membership `active` + org `active` (`organizations.services`).
- `User.status=blocked` implica `is_active=False` e impede autenticação (`users.models.User.save`).
- Vínculo `OrganizationMembership` é a fonte de verdade do tenant; API não aceita `organization_id` do client como escopo.
- Alterações Admin em user/org/membership geram `core.AuditLog` sem senha/token (`core.audit`).

## Inferidas e pendentes de confirmação

- Candidata a rule `2xx-business-identity-auto.mdc` a partir das regras confirmadas acima (Fase 2).

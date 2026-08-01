# Business Rules

Esta pasta serve como área auxiliar para documentar regras de negócio descobertas ou definidas no projeto.

Ela não substitui `.cursor/rules/*.mdc`.

## Arquivos

- `discovered-rules.md`: regras encontradas ou inferidas.
- `pending-questions.md`: dúvidas para o usuário/time.
- `decisions.md`: decisões confirmadas.

## Fluxo

1. Usar a skill `descobrir-regras-negocio` (rule stub `120-business-rules-discovery-manual.mdc`).
2. Registrar descobertas aqui.
3. Confirmar regras com o time.
4. Criar rule ativa em `.cursor/rules/2xx-business-<dominio>-auto.mdc`.

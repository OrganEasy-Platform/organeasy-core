# ADR 0002 — Multi-tenancy lógico por coluna (`organization_id`)

- **Status:** Aceito
- **Data:** 2026-08-03
- **Contexto:** Fase 0 — definição e limites (`organeasy-core`)

## Contexto

O OrganEasy é multi-organização (SaaS). Dados de negócio e de identidade vinculada ao tenant pertencem a uma organização. É necessário isolamento forte sem complexidade operacional prematura (um schema/banco por cliente desde o dia zero).

## Decisão

Adotar **multi-tenancy lógico por coluna**: entidades relevantes carregam `organization_id` (ou equivalente) e toda consulta/comando de negócio filtra pelo tenant ativo.

Regras obrigatórias:

- Cada requisição autenticada possui organização ativa (contexto de tenant).
- O `org_id` / `organization_id` do **token** (ou contexto resolvido no servidor) é a fonte de verdade.
- Nunca aceitar `organization_id` do body/query como substituto sem validar o vínculo do usuário.
- Índices compostos devem considerar `organization_id` nas tabelas mais consultadas.
- Testes negativos devem garantir que org A não lê/altera dados da org B.

Evolução para schema-por-tenant ou banco-por-tenant fica como **decisão futura**, não requisito do MVP do core.

## Alternativas consideradas

| Alternativa | Motivo de adiamento/rejeição (agora) |
| ----------- | ------------------------------------ |
| Schema por tenant (PostgreSQL) | Mais isolamento nativo, porém migrações, tooling e ops mais caros no início |
| Banco por tenant | Isolamento máximo; custo de provisionamento e observabilidade incompatível com o MVP |
| Tenant só via `Group` Django | Grupo global não identifica organização; viola o modelo multi-tenant do projeto |

## Consequências

- Simplicidade de infraestrutura (um PostgreSQL compartilhado no começo).
- Disciplina de código e testes de isolamento são obrigatórias — falha aqui vira vazamento cross-tenant.
- Helpers de contexto de tenant devem ser explícitos em services (Fase 4).

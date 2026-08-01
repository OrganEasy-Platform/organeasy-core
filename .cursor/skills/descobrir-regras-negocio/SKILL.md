---
name: descobrir-regras-negocio
description: Analisa o projeto Django/DRF existente para descobrir regras de negócio e propor rules 2xx-business. Use ao mapear código existente, antes de criar endpoints em domínios complexos ou quando uma regra nova for identificada durante desenvolvimento.
---

# Descobrir regras de negócio

## Objetivo

Analisar o diretório do projeto, identificar padrões reais de negócio e transformá-los em rules `.mdc` em `.cursor/rules/2xx-business-<dominio>-auto.mdc`.

Não substitui rules de arquitetura (000–130). Complementa com regras de domínio.

## Quando usar

- Projeto com módulos já implementados
- Regras espalhadas em views/serializers/services
- Novos endpoints devem respeitar regras existentes
- Regra nova descoberta ou definida com o usuário

## Arquivos prioritários

```text
<app>/models.py
<app>/views.py | viewsets.py
<app>/serializers.py
<app>/services/
<app>/permissions.py
core/
tests/
README.md
.env.example
```

## O que procurar

Fluxos principais, validações, transições de status, permissões e RBAC, isolamento por organização, módulos habilitados, normalizações, integrações obrigatórias, auditoria, campos imutáveis, erros HTTP esperados, efeitos colaterais (signals).

## Classificação (não inventar)

```text
Confirmada pelo código
Confirmada pelo README/documentação
Inferida com baixa confiança
Pergunta para o usuário
```

Rules novas **só** para regras confirmadas.

## Perguntas ao usuário (exemplos)

1. Algum status bloqueia edição/exclusão?
2. Quais papéis podem criar/editar/cancelar?
3. Campos com normalização obrigatória (upper, strip)?
4. Endpoint dispara integração externa ou evento?
5. Usuários administrativos veem todas as organizações?
6. Erros 400/403/404/409 esperados por contexto?

## `.cursor/business-rules/` (auxiliar)

- `discovered-rules.md` — rascunhos
- `pending-questions.md` — lacunas
- `decisions.md` — decisões confirmadas

Rules ativas ficam em `.cursor/rules/*.mdc`.

## Criar rule de negócio

Nome: `.cursor/rules/2xx-business-<dominio>-auto.mdc`

Globs por domínio, ex.:

```yaml
globs: "organizations/**/*.py,core/permissions.py"
alwaysApply: false
```

Conteúdo mínimo: Escopo, Regras obrigatórias, Fluxos, Permissões, Status, Validações, Integrações, Erros esperados, Testes, Fonte.

## Critérios para virar rule

- Aplicável em mais de um endpoint
- Protege regra importante / evita regressão
- Impacta permissão, status, integração, financeiro, auditoria

## Saída da análise

1. Módulos encontrados
2. Regras confirmadas
3. Regras inferidas (pendentes)
4. Perguntas
5. Rules sugeridas (nomes `.mdc`)
6. Próximos passos

**Não alterar código sem autorização explícita** — primeiro análise e composição de rules.

## Documentação após criar rule

- Atualizar `docs/cursor/rules-index.md`
- Atualizar `.cursor/business-rules/` se aplicável
- README do projeto + **Alterações recentes**

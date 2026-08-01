---
name: auditar-rules-skills-docs
description: Audita a organização de Cursor Rules, Skills e documentação do projeto. Use quando reorganizar rules, reduzir contexto global, migrar workflows para Skills ou validar links órfãos entre .cursor/rules, .cursor/skills e docs/cursor.
---

# Auditar Rules, Skills e Docs

## Objetivo

Mapear duplicação, rules gigantes, referências órfãs e oportunidades de enxugar contexto global sem quebrar comportamento do agente.

## Checklist de auditoria

```text
- [ ] Listar .cursor/rules/*.mdc (alwaysApply vs globs)
- [ ] Identificar duplicação entre rules globais (000, 010 e rules herdadas)
- [ ] Rules >150 linhas candidatas a Skill + stub
- [ ] Rules manuais (075, 120, 130) — já têm Skill?
- [ ] Rule gate 005-rule-vs-skill-gate-always.mdc existe?
- [ ] Links em AGENTS.md e docs/cursor/* válidos
- [ ] Skills em .cursor/skills/ com SKILL.md válido
- [ ] Rules 200–280 intactas (negócio não vira Skill)
- [ ] docs/cursor/rules-index.md atualizado
```

## Classificação por tipo

| Tipo | Onde fica | Exemplo |
|------|-----------|---------|
| Princípio global curto | rule `alwaysApply: true` | 000, 005, 080, 100 |
| Padrão por camada | rule com globs | 020–090 |
| Workflow longo | Skill + rule stub | CI, tarefas multi-camada |
| Negócio confirmado | rule 2xx | `2xx-business-*` |
| Índice/documentação | docs/cursor/ | rules-index.md |

## Gate Rule vs Skill

O projeto deve ter a rule global `005-rule-vs-skill-gate-always.mdc` (`alwaysApply: true`). Ela orienta o agente a **questionar o usuário** antes de criar uma rule quando o pedido na verdade deveria ser Skill.

**Ao final de cada auditoria** (ou ao detectar pedido de nova rule grande/operacional):

1. Verificar se `005-rule-vs-skill-gate-always.mdc` existe em `.cursor/rules/`.
2. Se não existir, propor ou criar a rule gate.
3. Se o usuário pediu criar rule e o conteúdo é workflow, sugerir Skill e aguardar confirmação.

## Saída esperada

1. Tabela: arquivo | linhas | ação (manter/encurtar/skill/docs)
2. Links órfãos encontrados
3. Plano em fases (quick wins → skills → enxugar → entry points)
4. Lista de arquivos a criar/mover/renomear

## Regras da refatoração

- Não remover instruções críticas sem destino (Skill ou docs).
- Stubs manuais: "Use a Skill X quando..."
- Manter rules de negócio 200–280 em `.cursor/rules/`.
- Atualizar README do projeto (Alterações recentes) após mudanças relevantes.

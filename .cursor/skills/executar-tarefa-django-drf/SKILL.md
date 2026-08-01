---
name: executar-tarefa-django-drf
description: Executa tarefas maiores no organeasy-core seguindo camadas View-Serializer-Service-Model e entrega estruturada. Use ao criar apps/módulos, refatorar endpoints, alterar models/serializers ou concluir features multi-arquivo.
---

# Executar tarefa Django + DRF

Antes de alterar código, identifique camadas impactadas: `urls`, `views`, `serializers`, `services`, `models`, `admin`, `core/`, `tests/`, `docs/`.

## Criar novo módulo/app

1. App Django (`startapp`) registrado em `INSTALLED_APPS`
2. Model (se tabela nova) + migration
3. Serializers (entrada e saída; separar Create/Update de Response quando divergirem)
4. Service com regra de negócio
5. View/ViewSet chamando o service, com `permission_classes` e filtro por organização
6. Registrar rota no router/`urls.py` (versionada em `/api/v1/`)
7. Admin (se aplicável)
8. Testes básicos (status, permissões, isolamento multi-tenant)
9. README + **Alterações recentes** se relevante

## Alterar endpoint existente

1. Verificar regra de negócio na view
2. Mover para service se necessário
3. Manter view leve
4. Ajustar testes da rota
5. Atualizar docs se mudar contrato (sinalizar breaking change)

## Alterar model/serializer

1. Avaliar impacto em serializers, services, views e admin
2. Gerar migration; explicar riscos se destrutiva
3. Campos sensíveis fora do serializer de resposta
4. Atualizar testes
5. README se mudar contrato

## Regras transversais

- View leve → service com negócio → model/query só dados
- Multi-tenant: filtrar por organização (rule `080-auth-multitenancy-always.mdc`)
- Atenção a N+1: `select_related`/`prefetch_related`
- Múltiplas escritas relacionadas: `transaction.atomic()`
- Não versionar secrets; novas variáveis vão para `.env.example`
- Testes unitários sem banco/API externa real; mockar integrações
- Regras de domínio: consultar `.cursor/rules/2xx-business-*`
- Abstrações reutilizáveis: avaliar `core/` (rule `115`)

## Saída ao finalizar

Explicar:

- arquivos criados, alterados, removidos
- regras/skills aplicadas
- comandos de migração e teste recomendados
- pendências reais

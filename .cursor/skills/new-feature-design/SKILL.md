---
name: new-feature-design
description: Guia o design specification-first de novas features (descoberta, modelagem de domínio, contratos de API, especificação de UX, prototipação visual, aprovação, implementação e validação). Use ao planejar ou implementar nova feature, módulo, model, endpoint, tela, workflow ou integração com comportamento de produto relevante.
---

# New Feature Design

Use esta skill sempre que o usuário pedir para criar, planejar, expandir ou modificar significativamente uma feature de produto.

Este é um workflow **specification-first**: não iniciar implementação só porque o usuário descreveu uma ideia geral. Primeiro transformar a ideia em uma especificação revisável e aprovada (gate: rule `007-feature-design-approval-always.mdc`).

## Objetivos

- O usuário entende e aprova a feature antes da implementação.
- Cada model e campo tem propósito de negócio explícito.
- Cada endpoint tem contrato revisado.
- Cada tela tem informações, ações, estados e permissões definidos.
- Fluxos de negócio são visíveis e compreensíveis.
- Suposições são expostas, não convertidas silenciosamente em código.
- A implementação segue a especificação aprovada; desvios voltam para aprovação.

## Fase 0 — Classificar o tamanho da feature

- **Pequena**: sem entidade persistente nova; um endpoint simples ou ajuste de tela; sem novas permissões, workflow multi-etapa ou integração externa. Usar especificação compacta.
- **Média**: um ou mais models; múltiplos endpoints; uma ou mais telas; permissões ou transições de estado; validações relevantes. Usar o workflow padrão.
- **Grande**: novo módulo/bounded context; múltiplos atores, sistemas ou integrações; transições de estado complexas; várias telas; processamento assíncrono; implicações multi-tenant; decisões arquiteturais significativas. Usar o workflow completo e propor artefatos de design separados.

O tamanho muda a profundidade da documentação, **não** a exigência de aprovação.

## Fase 1 — Entender o pedido

Inspecionar o código **antes** de perguntar. Buscar: models e tabelas relacionados; endpoints similares; serializers/schemas; services e use cases; permissões existentes; páginas e componentes frontend relacionados; diagramas e ADRs; testes; convenções de nomenclatura; padrões de auditoria, logging, métricas e tracing; fronteiras de organização/tenant; integrações existentes.

Depois resumir:

- **Intenção da feature**: problema resolvido, valor de negócio, usuários-alvo, resultado desejado, não-objetivos explícitos.
- **Contexto existente**: arquivos relevantes, entidades existentes, componentes reutilizáveis, features similares, restrições arquiteturais, conflitos potenciais.

Não perguntar ao usuário o que pode ser respondido inspecionando o repositório.

## Fase 2 — Atores e permissões

Criar matriz de atores:

| Ator ou papel | Ver | Criar | Editar | Excluir | Aprovar | Restrições |
| ------------- | --: | ----: | -----: | ------: | ------: | ---------- |

Confirmar: quem inicia o fluxo; quem vê a feature; quem executa cada ação; quem aprova ou cancela; qual organização é dona dos dados; se existe acesso cross-organização; se o sistema executa ações automáticas; se sistemas externos participam.

Permissão é parte do design de produto, não detalhe de implementação posterior.

## Fase 3 — Modelar o fluxo de negócio

Descrever: gatilho; pré-condições; fluxo principal de sucesso; fluxos alternativos; decisões; transições de estado; caminhos de falha e cancelamento; retry; notificações; integrações externas; resultados finais.

Para features com estado, montar tabela de estados:

| Estado atual | Ação | Ator | Condições | Próximo estado | Efeitos colaterais |
| ------------ | ---- | ---- | --------- | -------------- | ------------------ |

Propor artefato visual quando útil: Lucidchart para processos de negócio e fluxos de decisão; Mermaid para diagramas versionados no repositório; diagrama de sequência para interação entre serviços; diagrama de estados para entidades com ciclo de vida complexo. Sem integração direta disponível, gerar prompt pronto para colar na ferramenta escolhida.

## Fase 4 — Modelar os dados

Para cada entidade proposta:

**Responsabilidade**: o que representa; por que precisa existir; o que possui; o que não é responsabilidade dela; qual é a fonte da verdade.

**Dicionário de campos**:

| Campo | Tipo | Obrigatório | Default | Validação | Editável | Sensível | Propósito de negócio |
| ----- | ---- | ----------: | ------- | --------- | -------: | -------: | -------------------- |

Definir também: estratégia de chave primária; relacionamentos e cardinalidade; ownership e escopo de organização/tenant; unicidade; constraints de banco; índices; ciclo de vida; campos de auditoria; soft-delete/arquivamento; retenção; padrões de consulta esperados; concorrência; migração e backfill.

Pedir aprovação de **cada campo e seu propósito**. Nunca incluir campo só porque é comum em sistemas similares. Não gerar migration antes da aprovação do model.

## Fase 5 — Contratos de API

Para cada endpoint:

| Método | Rota | Propósito | Ator | Permissão |
| ------ | ---- | --------- | ---- | --------- |

Documentar:

- **Request**: parâmetros de path, query e headers; corpo; validação; campos obrigatórios e opcionais; exemplos.
- **Response**: schema de sucesso; status codes; paginação; metadados; exemplos.
- **Contrato de falha**: erros de validação, autenticação e autorização; not-found; conflitos; transições de estado inválidas; falhas de dependências externas; falhas com retry.
- **Comportamento**: fronteiras de transação; idempotência; concorrência; efeitos colaterais; eventos emitidos; webhooks; logs; métricas; traces; auditoria; rate limiting; compatibilidade.

Não implementar endpoint até o contrato ser aprovado. Não inventar campos de request/response sem aprovação.

## Fase 6 — Especificar telas e interações

Para cada tela:

- **Objetivo**: usuário-alvo; tarefa principal; pontos de entrada; resultado esperado.
- **Arquitetura de informação**: título; resumo; seções; tabelas; cards; abas; detalhes; informações de apoio.
- **Ações**:

| Ação | Disponível para | Pré-condições | Confirmação | Resultado | Destino |
| ---- | --------------- | ------------- | ----------- | --------- | ------- |

- **Listas**: colunas; filtros; busca; ordenação; agrupamento; paginação; visões salvas; ações em lote; exportação.
- **Formulários**:

| Campo | Componente | Obrigatório | Validação | Valor inicial | Regra de visibilidade |
| ----- | ---------- | ----------: | --------- | ------------- | --------------------- |

- **Estados de UI**: inicial; carregando; vazio; parcialmente carregado; sucesso; erro de validação; erro de servidor; permissão negada; desconectado; somente leitura; arquivado/excluído; processamento externo pendente.
- **Responsividade e acessibilidade**: comportamento mobile/tablet; navegação por teclado; gestão de foco; labels; anúncio de erros; contraste; salvaguardas de ações destrutivas.

Não decidir comportamento de produto com base apenas no que é mais fácil de implementar.

## Fase 7 — Escolher artefatos de prototipação

Recomendar conforme a incerteza dominante:

- **Lucidchart**: sequência de processo, decisões de negócio, atores, integrações entre sistemas, mudanças de estado, responsabilidades. Gerar tipo de diagrama, nós, conexões, decisões, lanes, labels e prompt pronto para colar.
- **Figma**: hierarquia de informação, layout de componentes, navegação, estados visuais, interação, responsividade. Gerar lista de telas, nomes de frames, componentes, variantes, anotações, links de navegação e design brief pronto para colar.
- **Lovable**: comparar alternativas de tela rapidamente, validar workflow interativo, testar navegação, protótipo visual descartável. Gerar prompt pronto com contexto de produto, usuários-alvo, telas, componentes, ações, estados, dados de exemplo, restrições, referências de design system e instrução explícita de que o protótipo **não** é fonte da verdade para contratos de backend.
- **Mermaid**: quando o diagrama deve viver no repositório, ser versionado, revisado em PR e sincronizado com a implementação. Criar o diagrama diretamente quando apropriado.

Nunca afirmar ter criado ou atualizado artefato externo sem a integração/ferramenta estar realmente disponível.

## Fase 8 — Observabilidade e auditoria

Confirmar: eventos de negócio a logar; logs técnicos e seus campos; campos sensíveis que **não** podem ser logados; métricas; traces; alertas; dashboards; registros de auditoria; identificação do ator; correlation IDs; monitoramento de integrações externas; indicadores de nível de serviço esperados.

Para fluxos críticos, definir como o suporte diagnosticará falhas.

## Fase 9 — Critérios de aceite

Criar critérios testáveis no formato:

```text
Dado [contexto inicial]
Quando [ação]
Então [resultado observável]
```

Cobrir: cenário principal de sucesso; permissões; validação; transições de estado; falhas; estados vazios; falhas externas; retries; isolamento de tenant; trilha de auditoria; observabilidade; acessibilidade quando aplicável.

## Fase 10 — Pacote de aprovação

Antes de implementar, apresentar:

1. Resumo executivo (o que será construído e por quê)
2. Escopo (incluído e excluído)
3. Atores e permissões
4. Fluxo de negócio (principal, alternativos, falhas)
5. Modelo de dados (entidades, campos, relacionamentos, constraints, ciclo de vida)
6. Contratos de API (rotas, schemas, erros, permissões, efeitos colaterais)
7. Especificação de telas (informações, ações, estados, navegação)
8. Artefatos visuais propostos (Lucidchart, Figma, Lovable, Mermaid)
9. Observabilidade e auditoria
10. Critérios de aceite
11. Decisões em aberto
12. Plano de implementação ordenado por dependência

Classificar cada decisão relevante como `Confirmado`, `Inferido`, `Aberto` ou `Fora de escopo`.

Encerrar com: `Aprovação necessária antes da implementação.`

## Fase 11 — Implementar apenas o escopo aprovado

Após aprovação explícita:

1. criar/atualizar testes;
2. criar camada de domínio e persistência;
3. criar migrations;
4. implementar services/use cases;
5. implementar contratos de API;
6. implementar permissões;
7. implementar telas de frontend;
8. adicionar auditoria e observabilidade;
9. atualizar diagramas e documentação;
10. rodar validação, testes, lint e type checks.

Seguir arquitetura e convenções do repositório (rules `010`, `080`, skill `executar-tarefa-django-drf`). Não modificar código não relacionado sem necessidade.

## Fase 12 — Parar em drift de especificação

Parar e voltar para aprovação quando: um campo novo se tornar necessário; um relacionamento precisar mudar; um contrato de endpoint precisar mudar; uma suposição de permissão for descoberta; uma nova tela ou ação for necessária; o fluxo tiver estado não modelado; uma integração se comportar diferente do esperado; um critério de aceite aprovado não puder ser atendido; a implementação exigir decisão arquitetural não aprovada.

Apresentar: problema descoberto; especificação afetada; opções; trade-offs; recomendação; decisão exigida do usuário.

## Fase 13 — Relatório final

Após implementar, reportar: arquivos criados e modificados; migrations; endpoints; telas; permissões; testes; diagramas; documentação; mudanças de observabilidade; desvios aprovados; riscos remanescentes; passos de validação manual.

Criar tabela de rastreabilidade:

| Requisito | Implementação | Teste | Status |
| --------- | ------------- | ----- | ------ |

A feature não está completa enquanto um requisito aprovado estiver sem implementação ou validação.

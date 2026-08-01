**OrganEasy**

Plano de implementação e arquitetura

**Django Core + Django REST Framework + SimpleJWT + módulos FastAPI**

*Documento mestre para orientar o desenvolvimento incremental, o portfólio no GitHub e a produção de conteúdo técnico no LinkedIn.*

Versão revisada - julho de 2026

# 1. Resumo executivo

O OrganEasy será desenvolvido como uma plataforma SaaS modular e multi-organização. O objetivo principal não é recriar todo o Odoo logo no primeiro ciclo, mas construir um produto evolutivo que comprove, de forma pública, competências que hoje aparecem apenas na experiência profissional: arquitetura, FastAPI, Django, integração entre serviços, segurança, Docker Swarm, HAProxy, observabilidade, testes, CI/CD e domínio de processos empresariais.

A principal decisão desta revisão é manter no Django toda a identidade da plataforma: usuários, organizações, autenticação, perfis, permissões, administração e configuração dos módulos. O Django REST Framework expõe os endpoints de identidade e o SimpleJWT emite os tokens. Os serviços FastAPI validam esses tokens e aplicam as regras de negócio dos módulos.

Essa escolha replica uma arquitetura com a qual Igor já possui experiência prática no Arancia e evita construir um mecanismo de autenticação paralelo apenas para o portfólio.

# 2. Objetivos

* Criar evidências públicas e verificáveis das competências descritas no currículo ATS.
* Construir algo funcional desde as primeiras fases, sem depender da conclusão de todos os módulos.
* Demonstrar capacidade de projetar, desenvolver, testar, implantar e operar uma plataforma.
* Gerar releases, estudos de caso e publicações técnicas em cada marco relevante.
* Manter o projeto preparado para evolução comercial, sem transformar isso em pré-requisito para o portfólio.

# 3. Princípios do projeto

* Produto evolutivo: cada fase deve resultar em uma versão demonstrável.
* Modularidade pragmática: começar com poucos serviços e extrair componentes somente quando houver justificativa.
* Identidade centralizada: Django é a fonte de verdade de usuários, organizações e permissões.
* Contrato explícito: APIs, eventos e claims devem ser documentados e versionados.
* Segurança por padrão: menor privilégio, expiração curta, rotação, auditoria e isolamento por organização.
* Observabilidade desde cedo: logs estruturados, métricas e traces entram antes dos módulos mais complexos.
* Documentação como parte da entrega: README, ADRs, OpenAPI, diagramas e exemplos de uso.
* Escopo controlado: chamadas de vídeo, folha de pagamento completa e contabilidade fiscal não entram no MVP.

# 4. Arquitetura de referência

Visão lógica simplificada:

|  |
| --- |
| Clientes web e mobile ↓ HAProxy / API Gateway ↓ Django Core (identidade, organizações, RBAC, administração e catálogo de módulos) ↓ ↓ APIs do Core Módulos FastAPI  Kanban | Chat | Financeiro | RH | WMS | TMS | E-commerce ↓ ↓ PostgreSQL / SQL Server | Redis | mensageria | armazenamento de arquivos ↓ Prometheus | Grafana | Loki | Tempo |

## 4.1 Responsabilidades do Django Core

* Cadastro, ativação, bloqueio e recuperação de usuários.
* Cadastro de organizações e vínculo entre usuário e organização.
* Papéis, permissões e políticas de acesso.
* Emissão, renovação e revogação de tokens JWT por meio do DRF e SimpleJWT.
* Administração via Django Admin.
* Catálogo de módulos, planos e recursos habilitados por organização.
* Auditoria de ações administrativas e alterações sensíveis.
* Endpoints internos para consulta de identidade quando claims não forem suficientes.

## 4.2 Responsabilidades dos módulos FastAPI

* Implementar regras de negócio específicas de cada módulo.
* Validar assinatura, emissor, audiência e expiração do JWT.
* Aplicar autorização baseada em claims e, quando necessário, consultar o serviço de identidade.
* Isolar dados por organização em todas as consultas e comandos.
* Publicar eventos de domínio e processar tarefas assíncronas.
* Expor documentação OpenAPI e contratos de integração.
* Gerar logs, métricas e traces correlacionáveis.

# 5. JWT: decisão e fluxo recomendado

Sim: mantendo o Django como provedor de identidade, a emissão do JWT deve ficar no Django REST Framework. O pacote SimpleJWT é uma opção adequada para access token, refresh token, rotação e blacklist. O FastAPI não autentica novamente o usuário; ele valida o token emitido pelo Django.

## 5.1 Fluxo

1. O cliente envia as credenciais para o endpoint de autenticação do Django.
2. O Django valida usuário, organização selecionada, estado da conta e políticas aplicáveis.
3. O SimpleJWT emite access token de curta duração e refresh token de maior duração.
4. O cliente envia o access token no cabeçalho Authorization para o gateway e para os módulos.
5. O serviço FastAPI valida assinatura, expiração, issuer, audience e claims obrigatórias.
6. O serviço extrai user\_id, organization\_id, roles/scopes e correlation\_id quando aplicável.
7. Antes de acessar o banco, o serviço aplica obrigatoriamente o filtro de organização.
8. Quando o access token expira, o cliente usa o refresh token no Django para obter um novo token.

## 5.2 Claims mínimas sugeridas

|  |  |  |
| --- | --- | --- |
| **Claim** | **Exemplo** | **Finalidade** |
| sub | ID imutável do usuário | Identificação do principal |
| org\_id | ID da organização ativa | Isolamento multi-tenant |
| roles | [admin, manager] | Autorização de alto nível |
| scopes | [kanban:read, kanban:write] | Permissões consumíveis pelos módulos |
| iss | organeasy-auth | Validação do emissor |
| aud | organeasy-services | Restringir os consumidores do token |
| jti | Identificador único | Revogação e auditoria |
| exp / iat | Datas do token | Expiração e rastreabilidade |

## 5.3 Assinatura e distribuição de chaves

Para o primeiro protótipo local, uma chave simétrica compartilhada pode simplificar o desenvolvimento. Para a arquitetura demonstrável e ambientes publicados, prefira assinatura assimétrica: o Django mantém a chave privada e os módulos recebem apenas a chave pública. Isso reduz o impacto de um serviço comprometido e evita que qualquer módulo possa emitir tokens válidos.

* Publicar a chave pública ou um endpoint JWKS quando a arquitetura estiver madura.
* Prever rotação de chaves com identificador kid no cabeçalho do token.
* Nunca versionar segredos no repositório.
* Evitar colocar grande volume de permissões no token; claims grandes tornam o token pesado e ficam desatualizadas até a expiração.
* Usar access token curto e refresh token com rotação e blacklist.

# 6. Estratégia multi-tenant

O primeiro modelo recomendado é multi-tenancy lógico por coluna, com organization\_id obrigatório nas entidades de negócio. É mais simples para o portfólio, permite uma única infraestrutura e evidencia disciplina de isolamento. A evolução para schema por tenant ou banco por tenant deve ser tratada como decisão futura, não como requisito inicial.

* Cada requisição autenticada deve possuir uma organização ativa.
* O organization\_id do token nunca deve ser substituído por um valor enviado livremente no corpo da requisição.
* Repositórios e serviços devem receber o contexto do tenant explicitamente.
* Testes devem garantir que um usuário da organização A não lê ou altera dados da organização B.
* Tarefas em background e eventos também precisam carregar o tenant\_id.
* Índices compostos devem considerar organization\_id nas tabelas mais consultadas.

# 7. Estratégia de repositórios

Começar com um monorepo favorece consistência e reduz custo operacional. A separação física em múltiplos repositórios só deve ocorrer quando a autonomia de implantação ou o volume do projeto justificarem.

|  |
| --- |
| organeasy/  apps/  django\_core/  kanban\_service/  notification\_worker/  packages/  python\_auth\_client/  observability/  shared\_contracts/  infra/  docker/  swarm/  haproxy/  monitoring/  docs/  adr/  architecture/  api/  tests/  contract/  end\_to\_end/  .github/workflows/ |

# 8. Roadmap consolidado

|  |  |  |
| --- | --- | --- |
| **Fase** | **Nome** | **Resultado principal** |
| 0 | Definição do produto | Visão, escopo, ADRs e backlog inicial |
| 1 | Fundação técnica | Monorepo, padrões, ambientes locais |
| 2 | Django Core | Usuários, organizações e Admin |
| 3 | Autenticação JWT | DRF, SimpleJWT e validação no FastAPI |
| 4 | Multi-tenancy | Contexto e isolamento por organização |
| 5 | RBAC | Papéis, escopos e autorização |
| 6 | Módulos habilitáveis | Catálogo, planos e feature flags |
| 7 | Observabilidade e CI/CD | Logs, métricas, traces e pipeline |
| 8 | Kanban MVP | Primeiro módulo de negócio completo |
| 9 | Notificações e eventos | Assíncrono e comunicação entre módulos |
| 10 | Chat MVP | WebSocket e mensagens internas |
| 11 | Financeiro MVP | Contas e fluxo de caixa |
| 12 | RH MVP | Colaboradores, equipes e ausências |
| 13 | WMS MVP | Estoque, movimentações e endereços |
| 14 | TMS MVP | Embarques, ocorrências e rastreio |
| 15 | E-commerce MVP | Catálogo, pedidos e integração |
| 16 | Hardening e portfólio | Segurança, carga, documentação e demonstração |

# Fase 0 - Definição do produto e limites

**Objetivo:** Transformar a ideia ampla em uma visão executável e impedir que o projeto vire um ERP infinito.

## Escopo técnico

* Escrever visão do produto, público-alvo e proposta de valor.
* Definir módulos previstos e classificar cada um como MVP, posterior ou fora de escopo.
* Criar mapa de capacidades e contexto de alto nível.
* Registrar as primeiras decisões arquiteturais em ADRs.
* Criar backlog macro com épicos, dependências e riscos.

## Entregáveis

* README principal com visão do OrganEasy.
* Documento de escopo e não escopo.
* ADRs iniciais: Django como IdP, monorepo, multi-tenancy por coluna e comunicação síncrona/assíncrona.
* Quadro público no GitHub Projects.

## Critérios de conclusão

* É possível explicar o produto em menos de dois minutos.
* Existe um MVP claro sem WMS, TMS, RH, Financeiro e e-commerce completos.
* Cada decisão estrutural possui justificativa e alternativa considerada.

## O que esta fase demonstra

* Pensamento de produto.
* Capacidade de recorte de escopo.
* Arquitetura orientada a decisões.

## Conteúdo para LinkedIn e GitHub

* Post: por que um ERP modular não deve começar como um ERP completo.
* Publicar o diagrama de contexto e o primeiro ADR.

# Fase 1 - Fundação técnica

**Objetivo:** Criar uma base reproduzível para que todos os serviços sigam os mesmos padrões.

## Escopo técnico

* Configurar monorepo, ambientes e comandos padronizados.
* Criar Django Core e um serviço FastAPI mínimo.
* Configurar lint, formatação, tipagem, testes e hooks locais.
* Criar Docker Compose para desenvolvimento.
* Definir convenções de logs, erros, versionamento de API e configuração por ambiente.

## Entregáveis

* Ambiente sobe com um único comando.
* Health checks do Django, FastAPI, banco e Redis.
* Pipeline inicial no GitHub Actions.
* Guia CONTRIBUTING e convenção de commits.

## Critérios de conclusão

* Novo desenvolvedor consegue executar o projeto seguindo apenas o README.
* PR falha quando lint, tipos ou testes falham.
* Nenhum segredo está versionado.

## O que esta fase demonstra

* Engenharia de plataforma.
* Padronização e experiência de desenvolvimento.
* Qualidade desde o início.

## Conteúdo para LinkedIn e GitHub

* Post: estrutura de um monorepo híbrido Django + FastAPI.
* Release v0.1.0 com ambiente local reproduzível.

# Fase 2 - Django Core

**Objetivo:** Construir a fonte de verdade administrativa e de identidade do OrganEasy.

## Escopo técnico

* Modelos de usuário, organização e associação usuário-organização.
* Django Admin customizado para operações essenciais.
* Estados de usuário e organização.
* Auditoria de alterações administrativas.
* API inicial em DRF para perfil e organizações disponíveis.

## Entregáveis

* Core administrativo funcional.
* Seeds ou fixtures para demonstração.
* Testes dos modelos e regras administrativas.
* Documentação do modelo de identidade.

## Critérios de conclusão

* Administrador cria organização, usuário e vínculo.
* Usuário visualiza apenas organizações às quais pertence.
* Alterações sensíveis geram registro de auditoria.

## O que esta fase demonstra

* Domínio de Django além de CRUD.
* Modelagem de identidade.
* Administração e governança.

## Conteúdo para LinkedIn e GitHub

* Vídeo curto mostrando o Django Admin do OrganEasy.
* Post: por que centralizar identidade no Django.

# Fase 3 - Autenticação JWT com DRF e SimpleJWT

**Objetivo:** Emitir tokens no Django e demonstrar autenticação integrada com FastAPI.

## Escopo técnico

* Endpoints de login, refresh, logout e consulta do usuário atual.
* Access token curto e refresh token com rotação.
* Blacklist de refresh tokens revogados.
* Claims de organização, papéis e escopos.
* Validação do JWT no FastAPI.
* Tratamento consistente de 401 e 403.
* Preparar assinatura assimétrica para ambientes publicados.

## Entregáveis

* Fluxo completo Django → token → FastAPI.
* Biblioteca interna reutilizável para validação do token.
* Testes de token expirado, inválido, revogado e com audience incorreta.
* Diagrama de sequência da autenticação.

## Critérios de conclusão

* FastAPI nunca consulta senha ou sessão do usuário.
* Token inválido não alcança a camada de negócio.
* Logout impede reutilização do refresh token revogado.
* Logs não exibem tokens completos.

## Riscos e cuidados

* Não usar a mesma chave privada em todos os serviços.
* Não confiar apenas na existência da claim; validar issuer, audience e expiração.
* Não armazenar dados mutáveis demais no JWT.

## O que esta fase demonstra

* Integração entre frameworks.
* Segurança de APIs.
* Autenticação centralizada.

## Conteúdo para LinkedIn e GitHub

* Post técnico com o fluxo de autenticação entre Django e FastAPI.
* Demo protegendo um endpoint FastAPI com token emitido pelo Django.

# Fase 4 - Multi-tenancy

**Objetivo:** Garantir isolamento lógico de dados desde o primeiro módulo.

## Escopo técnico

* Definir organização ativa no login ou por endpoint de troca de contexto.
* Propagar org\_id no JWT.
* Criar contexto de tenant no Django, FastAPI, workers e eventos.
* Adicionar organization\_id às entidades de negócio.
* Criar filtros e repositórios seguros por padrão.
* Implementar testes de isolamento entre tenants.

## Entregáveis

* Middleware/dependency de contexto do tenant.
* Pacote ou padrão compartilhado de consultas tenant-aware.
* Suíte de testes negativos de acesso cruzado.
* ADR sobre estratégia multi-tenant.

## Critérios de conclusão

* Nenhum endpoint aceita org\_id livremente para substituir o token.
* Consultas sem contexto de tenant falham de forma segura.
* Testes comprovam isolamento de leitura e escrita.

## O que esta fase demonstra

* SaaS multi-tenant.
* Segurança de dados.
* Modelagem para escala.

## Conteúdo para LinkedIn e GitHub

* Post: os erros mais perigosos em multi-tenancy por coluna.
* Teste demonstrativo de tentativa de acesso entre organizações.

# Fase 5 - RBAC e autorização

**Objetivo:** Centralizar políticas no Django e torná-las consumíveis pelos módulos.

## Escopo técnico

* Criar papéis padrão e customizados por organização.
* Mapear permissões para scopes de API.
* Adicionar escopos relevantes ao token.
* Criar dependency de autorização no FastAPI.
* Definir estratégia para permissões altamente dinâmicas.
* Auditar concessões e remoções de acesso.

## Entregáveis

* Matriz de permissões.
* Interface administrativa de papéis.
* Helpers de autorização para Django e FastAPI.
* Testes 401 versus 403 e menor privilégio.

## Critérios de conclusão

* Usuário sem permissão recebe 403.
* Mudanças críticas de permissão são auditadas.
* Escopos seguem nomenclatura consistente módulo:ação.

## O que esta fase demonstra

* RBAC real.
* Governança de acesso.
* Integração de autorização distribuída.

## Conteúdo para LinkedIn e GitHub

* Post: diferença entre autenticação, papel e escopo.
* Exemplo de uma mesma rota para perfis distintos.

# Fase 6 - Catálogo e habilitação de módulos

**Objetivo:** Permitir que cada organização habilite apenas os recursos necessários.

## Escopo técnico

* Modelar módulos, recursos, dependências e estados.
* Associar módulos habilitados à organização.
* Criar feature flags no backend.
* Bloquear rotas de módulos não habilitados.
* Exibir catálogo administrativo.
* Registrar eventos de ativação e desativação.

## Entregáveis

* Catálogo funcional.
* Endpoint de capacidades da organização.
* Dependency FastAPI para exigir módulo habilitado.
* Testes de ativação, desativação e dependências.

## Critérios de conclusão

* Desativar módulo bloqueia acesso sem apagar dados.
* Dependências são validadas.
* Frontend consegue descobrir capacidades pelo backend.

## O que esta fase demonstra

* Arquitetura modular.
* Feature flags.
* Design de produto SaaS.

## Conteúdo para LinkedIn e GitHub

* Post: como separar licença, permissão e feature flag.
* Release demonstrando organizações com módulos diferentes.

# Fase 7 - Observabilidade, CI/CD e ambiente publicado

**Objetivo:** Tornar o OrganEasy operável e demonstrar experiência DevOps.

## Escopo técnico

* Logs JSON com correlation\_id, user\_id e org\_id sem dados sensíveis.
* Métricas Prometheus por serviço e endpoint.
* Tracing distribuído com OpenTelemetry e Tempo.
* Dashboards Grafana e centralização no Loki.
* Pipelines de testes, build, análise e deploy.
* Stacks Docker Swarm, secrets e HAProxy.
* Estratégia de rollback e migração de banco.

## Entregáveis

* Ambiente de demonstração publicado.
* Dashboard de saúde do OrganEasy.
* Pipeline com versionamento de imagens.
* Runbook de deploy e rollback.
* Alertas básicos de indisponibilidade e erros.

## Critérios de conclusão

* Uma requisição pode ser seguida do gateway ao serviço.
* Deploy não usa latest como versão imutável.
* Falha de health check impede tráfego para réplica.
* Existe procedimento testado de rollback.

## O que esta fase demonstra

* Docker Swarm e HAProxy.
* Observabilidade completa.
* Entrega contínua e operação.

## Conteúdo para LinkedIn e GitHub

* Post com o caminho de uma requisição no Grafana, Loki e Tempo.
* Diagrama da infraestrutura e vídeo de deploy.

# Fase 8 - Kanban MVP

**Objetivo:** Entregar o primeiro módulo de negócio completo e utilizável.

## Escopo técnico

* Projetos, quadros, colunas, cartões e responsáveis.
* Ordenação e movimentação de cartões.
* Comentários, etiquetas, prazos e histórico.
* Filtros e paginação.
* Permissões por ação e isolamento por organização.
* Eventos para criação, movimentação e conclusão.

## Entregáveis

* API FastAPI documentada.
* Interface mínima funcional.
* Testes unitários, integração e ponta a ponta.
* Dados de demonstração.
* OpenAPI e coleção de requisições.

## Critérios de conclusão

* Usuário cria projeto e conduz um cartão até a conclusão.
* Histórico registra alterações relevantes.
* Métricas e traces aparecem no ambiente publicado.
* Cobertura dos fluxos críticos.

## O que esta fase demonstra

* FastAPI aplicado a domínio real.
* Modelagem e consistência transacional.
* Produto completo de ponta a ponta.

## Conteúdo para LinkedIn e GitHub

* Série de posts do desenho ao deploy.
* Estudo de caso no README com GIFs e arquitetura.

# Fase 9 - Eventos e notificações

**Objetivo:** Desacoplar efeitos secundários e preparar comunicação entre módulos.

## Escopo técnico

* Definir envelope padrão de eventos.
* Outbox transacional para eventos críticos.
* Worker de notificações.
* Notificações internas e preferências do usuário.
* Retentativas, idempotência e dead-letter quando aplicável.
* Tracing entre publicação e consumo.

## Entregáveis

* Contrato versionado de eventos.
* Worker e painel básico de falhas.
* Testes de idempotência.
* Notificação gerada por eventos do Kanban.

## Critérios de conclusão

* Reprocessar evento não duplica efeito.
* Falha temporária possui retentativa controlada.
* Evento contém tenant\_id e correlation\_id.

## O que esta fase demonstra

* Arquitetura orientada a eventos.
* Mensageria e confiabilidade.
* Integração assíncrona.

## Conteúdo para LinkedIn e GitHub

* Post: por que publicar evento dentro da mesma transação pode falhar.
* Demo do Kanban gerando notificação assíncrona.

# Fase 10 - Chat interno MVP

**Objetivo:** Adicionar comunicação em tempo real sem assumir o custo de videoconferência própria.

## Escopo técnico

* Conversas diretas e canais por organização.
* Mensagens persistidas e paginação de histórico.
* WebSocket autenticado.
* Indicadores de leitura e presença simplificada.
* Notificações de novas mensagens.
* Anexos com política de tamanho e tipo.
* Integração futura com provedor externo de reuniões por link.

## Entregáveis

* Chat funcional em duas sessões.
* Escalonamento horizontal documentado com Redis Pub/Sub ou equivalente.
* Testes de autorização em canais.
* Métricas de conexões e mensagens.

## Critérios de conclusão

* Usuário não acessa canal de outra organização.
* Reconexão não perde histórico persistido.
* Token expirado encerra ou renova acesso de forma definida.

## Riscos e cuidados

* Não construir infraestrutura própria de WebRTC como primeiro objetivo.
* Planejar limites de conexão e proteção contra abuso.

## O que esta fase demonstra

* WebSockets.
* Tempo real distribuído.
* Decisão buy versus build para vídeo.

## Conteúdo para LinkedIn e GitHub

* Post: chat em tempo real com FastAPI e Redis.
* Explicação de por que chamadas de vídeo ficam fora do MVP.

# Fase 11 - Financeiro MVP

**Objetivo:** Demonstrar regras financeiras sem tentar implementar contabilidade fiscal completa.

## Escopo técnico

* Contas a pagar e receber.
* Categorias e centros de custo.
* Baixas, vencimentos e recorrências simples.
* Fluxo de caixa e visão consolidada.
* Importação CSV e trilha de auditoria.

## Entregáveis

* API e interface mínima.
* Modelo de domínio documentado.
* Testes dos fluxos críticos.
* Integração com identidade, tenant, RBAC, eventos e observabilidade.

## Critérios de conclusão

* Fluxo principal pode ser demonstrado de ponta a ponta.
* Casos de erro e autorização estão testados.
* Módulo pode ser habilitado ou desabilitado por organização.

## O que esta fase demonstra

* Conhecimento de domínio empresarial.
* Integração entre módulos.
* Qualidade e consistência em sistemas reais.

## Conteúdo para LinkedIn e GitHub

* Post: decisões de modelagem do módulo Financeiro MVP.
* Release e vídeo de demonstração do Financeiro MVP.

# Fase 12 - RH MVP

**Objetivo:** Organizar pessoas e rotinas internas sem criar folha de pagamento.

## Escopo técnico

* Colaboradores, equipes e cargos.
* Documentos e contatos básicos.
* Solicitações de ausência e férias.
* Aprovações e calendário de equipe.
* Histórico de alterações.

## Entregáveis

* API e interface mínima.
* Modelo de domínio documentado.
* Testes dos fluxos críticos.
* Integração com identidade, tenant, RBAC, eventos e observabilidade.

## Critérios de conclusão

* Fluxo principal pode ser demonstrado de ponta a ponta.
* Casos de erro e autorização estão testados.
* Módulo pode ser habilitado ou desabilitado por organização.

## O que esta fase demonstra

* Conhecimento de domínio empresarial.
* Integração entre módulos.
* Qualidade e consistência em sistemas reais.

## Conteúdo para LinkedIn e GitHub

* Post: decisões de modelagem do módulo RH MVP.
* Release e vídeo de demonstração do RH MVP.

# Fase 13 - WMS MVP

**Objetivo:** Evidenciar experiência de logística e estoque com escopo controlado.

## Escopo técnico

* Produtos, depósitos e endereços.
* Saldo por endereço.
* Entradas, saídas, transferências e inventário.
* Reservas e rastreabilidade.
* Regras de consistência e concorrência.

## Entregáveis

* API e interface mínima.
* Modelo de domínio documentado.
* Testes dos fluxos críticos.
* Integração com identidade, tenant, RBAC, eventos e observabilidade.

## Critérios de conclusão

* Fluxo principal pode ser demonstrado de ponta a ponta.
* Casos de erro e autorização estão testados.
* Módulo pode ser habilitado ou desabilitado por organização.

## O que esta fase demonstra

* Conhecimento de domínio empresarial.
* Integração entre módulos.
* Qualidade e consistência em sistemas reais.

## Conteúdo para LinkedIn e GitHub

* Post: decisões de modelagem do módulo WMS MVP.
* Release e vídeo de demonstração do WMS MVP.

# Fase 14 - TMS MVP

**Objetivo:** Demonstrar conhecimento real de transportes, integrações e eventos operacionais.

## Escopo técnico

* Embarques, documentos e volumes.
* Transportadoras, motoristas e veículos simplificados.
* Ocorrências, status e rastreio.
* Webhooks e integrações simuladas.
* Indicadores de prazo e exceções.

## Entregáveis

* API e interface mínima.
* Modelo de domínio documentado.
* Testes dos fluxos críticos.
* Integração com identidade, tenant, RBAC, eventos e observabilidade.

## Critérios de conclusão

* Fluxo principal pode ser demonstrado de ponta a ponta.
* Casos de erro e autorização estão testados.
* Módulo pode ser habilitado ou desabilitado por organização.

## O que esta fase demonstra

* Conhecimento de domínio empresarial.
* Integração entre módulos.
* Qualidade e consistência em sistemas reais.

## Conteúdo para LinkedIn e GitHub

* Post: decisões de modelagem do módulo TMS MVP.
* Release e vídeo de demonstração do TMS MVP.

# Fase 15 - E-commerce MVP

**Objetivo:** Conectar catálogo e pedidos aos módulos operacionais.

## Escopo técnico

* Catálogo e variações.
* Clientes, carrinho e pedidos.
* Estados do pedido.
* Integração simulada de pagamento.
* Eventos para financeiro, WMS e TMS.

## Entregáveis

* API e interface mínima.
* Modelo de domínio documentado.
* Testes dos fluxos críticos.
* Integração com identidade, tenant, RBAC, eventos e observabilidade.

## Critérios de conclusão

* Fluxo principal pode ser demonstrado de ponta a ponta.
* Casos de erro e autorização estão testados.
* Módulo pode ser habilitado ou desabilitado por organização.

## O que esta fase demonstra

* Conhecimento de domínio empresarial.
* Integração entre módulos.
* Qualidade e consistência em sistemas reais.

## Conteúdo para LinkedIn e GitHub

* Post: decisões de modelagem do módulo E-commerce MVP.
* Release e vídeo de demonstração do E-commerce MVP.

# Fase 16 - Hardening, desempenho e apresentação final

**Objetivo:** Transformar o conjunto de fases em um portfólio fácil de avaliar.

## Escopo técnico

* Revisão de segurança e ameaças.
* Testes de carga dos endpoints críticos.
* Otimização de consultas e índices.
* Backup e restauração testados.
* Políticas de retenção e privacidade.
* Documentação C4 e ADRs consolidados.
* Landing page, ambiente demo e contas de teste.
* Estudo de caso relacionando o projeto à experiência profissional sem revelar informações privadas.

## Entregáveis

* Relatório de desempenho.
* Checklist de segurança.
* Documentação navegável.
* Vídeo de arquitetura e demonstração.
* README com screenshots, métricas, decisões e roadmap.
* Currículo e LinkedIn atualizados com links objetivos.

## Critérios de conclusão

* Recrutador entende o projeto em até cinco minutos.
* Ambiente demo possui dados fictícios e mecanismo de reset.
* Restauração de backup foi exercitada.
* Principais decisões possuem ADR.
* Nenhum dado ou código da empresa atual foi reutilizado.

## O que esta fase demonstra

* Visão de arquitetura e operação.
* Performance e segurança.
* Comunicação técnica e liderança.

## Conteúdo para LinkedIn e GitHub

* Artigo completo: construindo uma plataforma SaaS híbrida Django + FastAPI.
* Post final com resultados, aprendizados e próximos passos.

# 9. Definição de pronto

* Código revisado e integrado à branch principal.
* Testes automatizados dos fluxos críticos passando.
* Migrações de banco testadas em ambiente limpo.
* Documentação da API atualizada.
* Logs, métricas e traces relevantes disponíveis.
* Autorização e isolamento multi-tenant testados.
* README ou documentação da fase atualizado.
* Release e changelog publicados.
* Nenhum segredo, dado real da empresa ou informação sensível no repositório.

# 10. Estratégia de testes

|  |  |
| --- | --- |
| **Camada** | **Foco** |
| Unitários | Regras puras, serviços de domínio, validadores e políticas. |
| Integração | Banco, Redis, mensageria, autenticação e persistência. |
| Contrato | Compatibilidade entre Django, FastAPI, eventos e clientes. |
| E2E | Fluxos críticos do usuário em ambiente próximo ao real. |
| Segurança | Autorização, isolamento de tenant, tokens e entradas maliciosas. |
| Carga | Login, listagens, Kanban, chat e operações críticas de WMS/TMS. |

# 11. Estratégia para GitHub

* Manter README principal orientado a quem avalia o projeto, não apenas a quem desenvolve.
* Fixar releases relevantes e usar changelog.
* Usar Issues e GitHub Projects publicamente.
* Registrar decisões em docs/adr.
* Adicionar diagramas, GIFs curtos e screenshots.
* Evitar repositórios genéricos como estudo-fastapi; o OrganEasy deve concentrar a narrativa.
* Criar projetos satélites somente quando houver valor claro: SDK, CLI ou pacote de autenticação.

# 12. Estratégia para LinkedIn

* Publicar decisões e resultados, não apenas listas de tecnologias.
* Cada post deve conter problema, decisão, trade-off, implementação e evidência.
* Alternar conteúdo de arquitetura, backend, DevOps, testes e domínio logístico.
* Usar diagramas e pequenos vídeos de demonstração.
* Relacionar aprendizados ao OrganEasy sem revelar detalhes confidenciais do Arancia ou da empresa.
* Atualizar a seção Projetos do LinkedIn quando Kanban, observabilidade e primeiro módulo logístico estiverem públicos.

# 13. Ordem prática recomendada

1. Concluir as fases 0 a 3 antes de iniciar qualquer módulo de negócio.
2. Concluir multi-tenancy, RBAC e habilitação de módulos antes do Kanban.
3. Publicar observabilidade e CI/CD junto do primeiro módulo, não no fim do projeto.
4. Usar o Kanban como prova de ponta a ponta.
5. Adicionar eventos e notificações antes do chat.
6. Tratar Financeiro e RH como módulos intermediários.
7. Reservar WMS e TMS para a etapa em que a base já esteja estável, pois serão os módulos que melhor conectam o portfólio à experiência profissional.
8. Adicionar e-commerce apenas depois de existirem contratos estáveis de estoque, pedidos e transporte.

# 14. Primeira entrega recomendada

O primeiro marco público não deve ser “ERP pronto”. Deve ser a release Foundation, contendo monorepo, Django Core, serviço FastAPI protegido por JWT, uma organização de demonstração, RBAC inicial, ambiente Docker reproduzível, pipeline e diagrama de arquitetura. Essa entrega já prova integração entre Django e FastAPI e estabelece a base para os demais chats e fases.

# 15. Checklist para iniciar cada novo chat

* Informar o número e o nome da fase.
* Anexar ou citar este documento como referência.
* Descrever o estado atual do repositório.
* Listar decisões já tomadas que não devem ser alteradas.
* Pedir um plano de execução com tarefas, critérios de aceite, estrutura de pastas e testes.
* Ao final, atualizar README, ADRs, changelog e quadro do GitHub.

# Conclusão

A arquitetura Django Core + DRF + SimpleJWT + módulos FastAPI é coerente com a experiência já adquirida no Arancia e cria uma narrativa técnica mais forte do que implementar autenticação separadamente em cada serviço. O sucesso do OrganEasy dependerá menos da quantidade de módulos e mais da qualidade das decisões, da documentação, das evidências públicas e da capacidade de entregar cada fase como um incremento real e demonstrável.
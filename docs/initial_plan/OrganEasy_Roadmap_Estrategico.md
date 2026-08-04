# OrganEasy - Roadmap Estratégico

> **Aviso (2026-08-03):** documento histórico de visão de alto nível. A stack do **núcleo** abaixo (FastAPI/SQLAlchemy como IdP) está **desatualizada**.
>
> - Documento mestre: [OrganEasy_Plano_de_Implementacao_Revisado.md](OrganEasy_Plano_de_Implementacao_Revisado.md)
> - Reconciliação: [roadmap-reconciliation.md](roadmap-reconciliation.md)
> - Neste repositório: Django + DRF + SimpleJWT = identidade; FastAPI = módulos de negócio (fora do core por enquanto)

Documento guia para desenvolvimento do OrganEasy como plataforma SaaS modular voltada a demonstrar competências em arquitetura de software, backend, infraestrutura e liderança técnica.

## Visão

Construir uma plataforma SaaS multi-tenant modular, desenvolvida com padrões de produção.

## Objetivos

Demonstrar arquitetura, FastAPI, Docker, observabilidade, testes, CI/CD e módulos de negócio.

## Stack

~~FastAPI, SQLAlchemy, Alembic~~ como núcleo — **substituído** no plano revisado por **Django + DRF + SimpleJWT** (IdP). FastAPI permanece para módulos de negócio.

Demais peças de plataforma (ainda válidas como direção): PostgreSQL/SQL Server, Redis, RabbitMQ, Docker Swarm, HAProxy, Grafana, Prometheus, Loki, Tempo, GitHub Actions.

## 1. Fundação

Estrutura do repositório, convenções, Clean Architecture, documentação.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 2. Infraestrutura

Docker Swarm, HAProxy, CI/CD, monitoramento.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 3. Autenticação

JWT, refresh token, usuários.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 4. Multi-tenancy

Organizações, isolamento de dados.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 5. RBAC

Perfis e permissões.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 6. Sistema de módulos

Feature flags e habilitação de módulos.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 7. Dashboard

Página inicial configurável.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 8. Kanban

Projetos, tarefas, comentários.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 9. Chat

WebSocket, salas, chamadas futuras.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 10. Notificações

Eventos e notificações.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 11. Agenda

Calendário e reuniões.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 12. Financeiro

Contas, fluxo de caixa.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 13. RH

Colaboradores e férias.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 14. WMS

Estoque e endereçamento.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 15. TMS

Transportes e entregas.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 16. E-commerce

Pedidos e catálogo.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 17. Integrações

APIs públicas, webhooks.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 18. Observabilidade

Logs, métricas, traces.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 19. Testes

Unitários, integração, E2E.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## 20. Produção

Escalabilidade, backup, hardening.

Entregáveis:
• Funcionalidade concluída
• Documentação
• Testes
• Post no LinkedIn
• README atualizado

## Boas práticas

- Commits pequenos
- Releases por fase
- Issues e Projects
- Documentação arquitetural
- Código com padrão de produção
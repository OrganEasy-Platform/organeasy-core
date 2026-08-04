# AGENTS.md - organeasy-core

Serviço de identidade da plataforma OrganEasy: Django + Django REST Framework, SimpleJWT, usuários, organizações (multi-tenancy), permissões, módulos habilitados, auditoria e Django Admin.

Regras principais:

- Views da API são function-based (`@api_view`), enxutas; regras complexas vão para services.
- Serializers validam entrada e definem contrato de saída; campos sensíveis fora da resposta.
- Models representam dados e relacionamentos, com constraints e índices.
- Todo endpoint declara autenticação e permissão explicitamente.
- Toda rota nova de API alimenta OpenAPI/Swagger (`drf-spectacular`, `/api/docs/` e `/api/schema/`; rule `065-openapi-swagger-auto.mdc`).
- Nunca assumir que `Group`/permissão global identifica a organização do usuário; filtrar dados pela organização real (rule `080-auth-multitenancy-always.mdc`).
- Persistir datas em UTC (`USE_TZ=True`, `timezone.now()`).
- Atenção a N+1: `select_related`/`prefetch_related`; paginação em listas.
- Não versionar secrets; novas variáveis de ambiente vão para `.env.example`.
- Ao descobrir regra de negócio recorrente, registrar e propor nova rule em `.cursor/rules/2xx-business-<dominio>-auto.mdc`.

Índice de rules e skills: `docs/cursor/rules-index.md`.

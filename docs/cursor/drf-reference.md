# Referência DRF — estrutura e padrões

Referência longa de estrutura e padrões para APIs Django REST Framework neste projeto. Consultar ao criar novos apps/módulos. Princípios curtos e obrigatórios ficam em `.cursor/rules/`.

## Estrutura de app

```text
app_name/
├── migrations/        # Migrations do banco
├── admin.py           # Configuração do Django Admin
├── apps.py            # Configuração do app
├── models.py          # Models
├── managers.py        # Managers customizados
├── signals.py         # Django signals
├── tasks.py           # Tarefas Celery (se aplicável)
└── __init__.py
```

## Estrutura de API

```text
api/
└── v1/
    ├── app_name/
    │   ├── urls.py            # Roteamento
    │   ├── serializers.py     # Serialização
    │   ├── views.py           # Views da API
    │   ├── permissions.py     # Permissões customizadas
    │   ├── filters.py         # Filtros customizados
    │   └── validators.py      # Validadores customizados
    └── urls.py                # URLs principais da API
```

## Estrutura core

```text
core/
├── responses.py       # Estruturas de response unificadas
├── pagination.py      # Paginação customizada
├── permissions.py     # Permissões base
├── exceptions.py      # Exception handler customizado
├── middleware.py      # Middlewares customizados
├── logging.py         # Logging estruturado
└── validators.py      # Validadores reutilizáveis
```

## Estrutura de configuração

```text
config/
├── settings/
│   ├── base.py        # Settings base
│   ├── development.py # Desenvolvimento
│   ├── staging.py     # Homologação
│   └── production.py  # Produção
├── urls.py            # URLs principais
└── wsgi.py
```

## Padrões

### Views e API
- Function-based views com DRF (`@api_view`); não usar `APIView` / `ViewSet` / `generics` em endpoints novos.
- Rotas com `path()` (sem `DefaultRouter` para recursos novos).
- REST estrito: métodos HTTP e status codes corretos.
- Views leves; negócio em services/models/managers.
- Response unificada para sucesso e erro.

### Models e banco
- ORM first; raw SQL só com justificativa de performance.
- `select_related`/`prefetch_related` para relacionamentos.
- Índices para campos consultados com frequência.
- `transaction.atomic()` em operações críticas.
- Signals para desacoplar efeitos colaterais (auditoria, notificações).

### Autenticação e permissões
- JWT com `djangorestframework-simplejwt`.
- Permission classes granulares por papel.
- CSRF, CORS e sanitização de entrada configurados corretamente.

### Performance
- Paginação padronizada em todos os endpoints de listagem.
- Cache (Redis) para dados acessados com frequência.
- Monitorar contagem de queries em desenvolvimento (N+1).
- Compressão de resposta para payloads grandes.

## Formato unificado de erro

```json
{
    "success": false,
    "message": "Descrição do erro",
    "errors": {
        "field_name": ["Detalhes específicos do erro"]
    },
    "error_code": "SPECIFIC_ERROR_CODE"
}
```

- Exception handler global para respostas de erro consistentes.
- Status HTTP adequados (400, 401, 403, 404, 409, 422, 500).

## Logging

- Logging estruturado para monitoramento e debug.
- Logar chamadas de API com tempo de execução, usuário e status.
- Logar queries lentas e gargalos de performance.
- Nunca logar senhas, tokens ou dados sensíveis.

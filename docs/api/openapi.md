# OpenAPI / Swagger — organeasy-core

Documentação interativa da API com **drf-spectacular** (OpenAPI 3).

## Rotas

| URL | Descrição |
| --- | --------- |
| [`/api/docs/`](http://127.0.0.1:8000/api/docs/) | Swagger UI |
| [`/api/schema/`](http://127.0.0.1:8000/api/schema/?format=json) | Schema OpenAPI (JSON/YAML) |

Ficam **fora** de `/api/v1/` — docs transversais à versão da API de negócio.

## Quando ligar / desligar

Controlado por `DJANGO_ENABLE_API_DOCS`:

| Ambiente | Default |
| -------- | ------- |
| `development` | `true` (se a variável não estiver no `.env`) |
| `test` / CI | `true` |
| `production` / `staging` / base | `false` (só liga com valor explícito) |

Em produção, só habilite com decisão explícita de segurança (rede, auth ou proxy).

```env
DJANGO_ENABLE_API_DOCS=true
```

## Como documentar um endpoint novo

1. Criar a FBV com `@api_view` + `path()` (rules `020` e `060`).
2. Anotar com `@extend_schema` (tags, summary, request/responses).
3. Usar serializers reais; para o envelope `{success, data}`, usar helpers em `core/openapi.py`.

Exemplo:

```python
from drf_spectacular.utils import extend_schema
from core.openapi import error_envelope, success_envelope

@extend_schema(
    tags=["me"],
    summary="Perfil do usuário autenticado",
    responses={
        200: success_envelope(MeSerializer(), name="MeSuccessResponse"),
        401: error_envelope(name="MeUnauthorized"),
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    ...
```

Rule do agente: `.cursor/rules/065-openapi-swagger-auto.mdc`.

## Autenticação no schema

A autenticação atual (`SessionAuthentication401`) aparece como `cookieAuth` (cookie `sessionid`), via extensão em `core/openapi.py`.

## Arquivos principais

| Arquivo | Papel |
| ------- | ----- |
| `config/urls.py` | Registra `/api/schema/` e `/api/docs/` quando a flag está on |
| `config/settings/base.py` | `DEFAULT_SCHEMA_CLASS`, `SPECTACULAR_SETTINGS`, `ENABLE_API_DOCS` |
| `core/openapi.py` | Envelopes + extensão de autenticação |
| `api/v1/*/views.py` | `@extend_schema` por endpoint |
| `api/v1/test_openapi.py` | Smoke do schema e da UI |

## Teste rápido

```bash
python manage.py runserver
# abrir http://127.0.0.1:8000/api/docs/

pytest api/v1/test_openapi.py -q
```

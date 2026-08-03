---
name: revisar-pr
description: Revisa pull requests ou diffs locais sob quatro ângulos (segurança, performance, testes, arquitetura), com severidade e citação de arquivo/linha. Adaptada ao Django/DRF multi-tenant do organeasy-core. Use quando o usuário pedir review de PR, diff ou "revisar este PR".
---

# Revisar PR / diff

Complementa `080-auth-multitenancy-always.mdc`, `100-security-settings-always.mdc`, `010-django-architecture-always.mdc` e `090-tests-auto.mdc`.

Quando o usuário pedir review de PR, conjunto de mudanças ou "este PR", escolher o ângulo adequado. Se enfatizar "segurança", "perf", "testes" ou "arch", usar esse ângulo. Se não especificar, perguntar ou defaultar para segurança.

## Disciplina de saída (todos os ângulos)

- Citar caminho do arquivo e número de linha em cada achado.
- Ranquear por severidade: `blocker`, `important`, `nit`.
- Ser específico. "Isso parece arriscado" não é achado; "views.py:42 — queryset sem filtro por organização" é.
- Se o diff não der contexto suficiente, declarar e pedir o arquivo completo.
- Encerrar com veredito em linha própria: `Safe to merge | needs changes | reject`.

Se o usuário colar só o diff, pedir o arquivo completo quando o risco estiver duas linhas fora da mudança.

---

## Ângulo 1: SEGURANÇA

Prioridade:

1. **Auth/authz** — endpoints ou branches novos sem autenticação/`permission_classes`; papéis assumidos; IDOR.
2. **Multi-tenancy (OrganEasy)** — queryset sem filtro pela organização do usuário; `organization_id` do payload aceito sem validar vínculo; exposição cross-tenant; ação de módulo sem checar módulo habilitado.
3. **Validação de entrada** — input não confiável em queries, shell, paths de arquivo ou deserialização.
4. **Injection** — SQL raw concatenado, command injection, template injection.
5. **Secrets** — chaves/tokens hardcoded; secrets em logs; `.env` commitado; `SECRET_KEY` real em settings.
6. **Exposição de dados** — PII em logs; response com campos sensíveis demais; falta de redaction.

Focar em defeitos, não nice-to-haves.

---

## Ângulo 2: PERFORMANCE

Foco Django/DRF:

1. **N+1** — loops acessando relações sem `select_related` / `prefetch_related`.
2. **Query em loop** — `Model.objects.get/filter` dentro de `for` sem batch.
3. **Listas sem paginação** — endpoints de lista retornando queryset ilimitado.
4. **Trabalho ilimitado** — agregações ou exports sem limite; recursão sem teto.
5. **Cache** — chaves incompletas; TTL ausente ou patológico; cache sem invalidação quando o dado muda.
6. **Índices** — filtros/joins/ordenções frequentes sem índice sugerido.

Citar a linha, nomear o padrão ruim e sugerir o fix.

---

## Ângulo 3: TESTES

1. **Cobertura de caminhos novos** — cada branch novo com pelo menos um teste.
2. **Casos de borda** — input vazio, `None`, limites, erros de dependências.
3. **Força das asserções** — asserts que passam com valor errado; só happy path.
4. **Mocking** — mocks que não falham se a interface real mudar; over-mocking.
5. **Determinismo** — data/hora/random/rede sem stub (risco de flake).
6. **Multi-tenant nos testes** — cenários que garantem isolamento entre organizações quando o endpoint é multi-tenant.
7. **Nomes** — nomes que descrevem comportamento.

Um teste que existe não é o mesmo que um teste que pega regressão. Ler as asserções.

---

## Ângulo 4: ARQUITETURA

1. **Boundary drift** — view com regra de negócio pesada; serializer com orquestração; model com fluxo de API (violação das camadas View → Serializer → Service → Model).
2. **Abstração prematura** — interfaces/factories/config com uma só implementação.
3. **Acoplamento** — utils importando de features; estado mutável compartilhado novo.
4. **Escalabilidade** — se o path for 10x, o que quebra primeiro?
5. **Reversibilidade** — portas de mão única (migrations destrutivas, contratos públicos) devem ser apontadas.
6. **Nomenclatura** — tipos/funções nomeados pela implementação, não pelo papel.

Encerrar o ângulo de arquitetura com: `Architecturally sound | needs trim | re-think before merging`.

---

## Checklist rápido multi-tenant

Antes do veredito de segurança, conferir:

- [ ] Autenticação explícita no endpoint
- [ ] `permission_classes` declaradas
- [ ] Organização resolvida pelo vínculo do usuário (não só pelo payload)
- [ ] Queryset filtrado pela organização
- [ ] Sem vazamento de dados de outra organização na response

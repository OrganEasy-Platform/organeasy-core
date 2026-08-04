# ADR 0004 — Comunicação síncrona agora; eventos/outbox depois

- **Status:** Aceito
- **Data:** 2026-08-03
- **Contexto:** Fase 0 — definição e limites (`organeasy-core`)

## Contexto

Entre o IdP (Django) e futuros módulos FastAPI haverá necessidade de integração. Mensageria, outbox e eventos de domínio são desejáveis em escala, mas introduzem infraestrutura (broker, workers, idempotência, DLQ) antes do core de identidade estar estável.

## Decisão

**Agora (Fases 0–6 do core):**

- Comunicação **síncrona** via HTTP/HTTPS e JWT.
- Módulos validam o token localmente (assinatura, `iss`, `aud`, `exp`, claims).
- Quando claims não bastarem, consultas pontuais ao core por API autenticada (endpoints internos de identidade), com cuidado de latência e cache.

**Depois (após core estável / fases posteriores do plano revisado):**

- Eventos de domínio, outbox e processamento assíncrono (Celery/broker conforme necessidade).
- Correlação (`correlation_id` / `jti`) já prevista nos contratos para facilitar a transição.

## Alternativas consideradas

| Alternativa | Motivo de adiamento |
| ----------- | ------------------- |
| Event-driven desde o dia zero | Custo de ops e complexidade sem consumidores reais ainda |
| Shared database entre core e módulos | Acoplamento forte; quebra limites de serviço |
| GraphQL federation | Fora do escopo e da stack decidida para o MVP |

## Consequências

- Menos peças na Fase 1 (Compose foca Django + PostgreSQL + Redis).
- Design de APIs do core deve ser estável o bastante para chamadas síncronas.
- Quando eventos entrarem, preferir outbox transacional a publicar direto na mesma request de escrita crítica.

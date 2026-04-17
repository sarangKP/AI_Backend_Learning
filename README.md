# AI_Backend_Learning
A containerized FastAPI service running alongside Ollama (serving a local LLM like Llama 3.1 or Qwen 2.5), doing RAG with pgvector, with auth, rate limiting, structured logging, Prometheus metrics, deployed via docker-compose and optionally Kubernetes. Zero API costs, full control.

# RAG Microservice — Project PRD

A self-hosted Retrieval-Augmented Generation (RAG) service built with FastAPI, Ollama (local LLM), and pgvector. Zero external API costs. Full stack ownership — from HTTP routing down to model serving.

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| API Framework | FastAPI | Async HTTP, routing, dependency injection |
| LLM Server | Ollama | Local model serving (llama3.2:3b) |
| Embeddings | Ollama / nomic-embed-text | 768-dim text vectors |
| Vector Store | PostgreSQL + pgvector | Similarity search with cosine distance |
| ORM | SQLAlchemy (async) | Async DB queries |
| Config | pydantic-settings | Typed, validated environment config |
| HTTP Client | httpx | Async calls to Ollama |
| Containers | Docker + docker-compose | Local orchestration |
| Auth | FastAPI Header dependency | API key validation |
| Rate Limiting | slowapi | Per-key request throttling |
| Logging | structlog | Structured JSON logs with request tracing |
| Metrics | prometheus-fastapi-instrumentator | `/metrics` endpoint for Prometheus |
| Tests | pytest + httpx.AsyncClient | Async integration tests |
| CI/CD | GitHub Actions | Test → build → push → deploy |

---

## Project Structure

```
AI_Backend_v2/
├── rag_service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app factory
│   │   ├── config.py            # Settings via pydantic-settings
│   │   ├── models.py            # Pydantic request/response schemas
│   │   ├── db.py                # SQLAlchemy engine + session factory
│   │   ├── routers/
│   │   │   ├── health.py        # GET /health
│   │   │   ├── chat.py          # POST /chat (streaming RAG)
│   │   │   └── documents.py     # POST /documents (ingest)
│   │   └── services/
│   │       ├── ollama_client.py # Ollama HTTP wrapper (chat + embed)
│   │       ├── embeddings.py    # Embed text via Ollama
│   │       └── retrieval.py     # pgvector similarity search
│   ├── db/
│   │   └── init.sql             # pgvector extension + table + index
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_health.py
│   │   ├── test_documents.py
│   │   └── test_chat.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
├── pyproject.toml
└── README.md                    # (this file)
```

---

## Build Plan — Block by Block

### DAY 1 — Core Service

---

#### Block 0 — Environment Setup
**Goal:** Ollama running, models pulled, `uv` installed, git initialized.

- [ ] `ollama pull llama3.2:3b`
- [ ] `ollama pull nomic-embed-text`
- [ ] Confirm `uv` is installed
- [ ] Repo on GitHub with initial commit

---

#### Block 1 — FastAPI Foundation
**Goal:** A running FastAPI server with two working endpoints.

**Files touched:**
| File | What gets built |
|---|---|
| `app/config.py` | `Settings` class + `get_settings()` with `lru_cache` |
| `app/models.py` | `HealthResponse`, `EchoRequest`, `EchoResponse` Pydantic models |
| `app/routers/health.py` | `GET /health` router |
| `app/main.py` | FastAPI app factory, router registration |

**Checkpoint:** `uvicorn` starts, `/health` and `/docs` reachable in browser.

---

#### Block 2 — Postgres + pgvector + Docker Compose
**Goal:** Full local infrastructure running via `docker compose up`.

**Files touched:**
| File | What gets built |
|---|---|
| `db/init.sql` | `CREATE EXTENSION vector`, documents table, ivfflat index |
| `app/db.py` | Async SQLAlchemy engine, `AsyncSession` factory, `get_db` dependency |
| `docker-compose.yml` | postgres, ollama, app services with healthchecks and volumes |
| `.env.example` | All required environment variables documented |

**Checkpoint:** `docker compose up postgres ollama` → `psql` confirms table + extension exist. `curl http://localhost:11434/api/tags` returns models.

---

#### Block 3 — Ollama Client + Streaming Chat Endpoint
**Goal:** `POST /chat` streams token-by-token responses from the local LLM.

**Files touched:**
| File | What gets built |
|---|---|
| `app/services/ollama_client.py` | `OllamaClient` class: `chat()` streaming, `embed()`, retry logic |
| `app/models.py` | `ChatRequest`, `ChatResponse` schemas |
| `app/routers/chat.py` | `POST /chat` with `StreamingResponse` + SSE format |

**Concepts covered:** NDJSON streaming, SSE format (`data: ...\n\n`), `tenacity` retry on transient errors, token count logging.

**Checkpoint:** `curl -N` streams tokens live. Logs show `input_tokens` and `output_tokens` per request.

---

#### Block 4 — RAG Pipeline: Ingest + Retrieve
**Goal:** Ingest documents, embed them, retrieve by cosine similarity, inject into LLM context.

**Files touched:**
| File | What gets built |
|---|---|
| `app/services/embeddings.py` | `embed_text()` calling Ollama's `/api/embeddings` |
| `app/services/retrieval.py` | `ingest_chunks()` and `retrieve_similar()` using pgvector |
| `app/routers/documents.py` | `POST /documents` — chunk, embed, store |
| `app/routers/chat.py` | Updated: embed query → retrieve → inject context → stream |
| `app/models.py` | `IngestRequest`, `IngestResponse`, `SourceChunk` schemas |

**Concepts covered:** Text chunking strategy, why embedding model must match on ingest + query, `<=>` cosine distance operator, context injection into system prompt.

**Checkpoint:** Ingest a markdown file → ask a question about it → response cites source chunks.

---

#### Block 5 — Dockerize + Tests + First Commit
**Goal:** Full stack runs in Docker. Tests pass. Clean git history.

**Files touched:**
| File | What gets built |
|---|---|
| `Dockerfile` | Single-stage build using `uv` |
| `tests/conftest.py` | `AsyncClient` fixture, mock factories |
| `tests/test_health.py` | `test_health_returns_200` |
| `tests/test_documents.py` | `test_ingest_document` with mocked embed |
| `tests/test_chat.py` | `test_chat_with_rag` with mocked embed + ollama |

**Checkpoint:** `docker compose up --build` — all three services healthy. `pytest` passes locally.

---

### DAY 2 — Production Hardening

---

#### Block 6 — Auth + Rate Limiting + CORS
**Goal:** Protect all endpoints with API key auth and per-key rate limits.

**Files touched:**
| File | What gets built |
|---|---|
| `app/auth.py` | `verify_api_key` dependency using `secrets.compare_digest` |
| `app/main.py` | `slowapi` limiter, CORS middleware, apply auth to routers |
| `app/config.py` | `api_key`, `allowed_origins`, `rate_limit_per_minute` settings |

**Concepts covered:** Timing attacks, `secrets.compare_digest` vs `==`, CORS preflight, rate limit key functions.

**Checkpoint:** Request without header → 401. Exceed 10 req/min → 429. OPTIONS preflight → 200.

---

#### Block 7 — Observability: Structured Logging + Prometheus
**Goal:** Every request produces a JSON log with trace ID. `/metrics` exports Prometheus data.

**Files touched:**
| File | What gets built |
|---|---|
| `app/logging.py` | `structlog` configuration, JSON renderer |
| `app/middleware.py` | Request ID middleware — generates + attaches UUID to each request |
| `app/main.py` | Wire in middleware, `prometheus-fastapi-instrumentator` |
| `docker-compose.yml` | Add `prometheus` and `grafana` services |

**Concepts covered:** Structured vs unstructured logs, trace IDs for request correlation, Prometheus pull model, P95 latency histograms.

**Checkpoint:** `curl /chat` → JSON log line with `request_id`, `latency_ms`, `tokens`. `curl /metrics` → valid Prometheus exposition format.

---

#### Block 8 — Multi-Stage Dockerfile
**Goal:** Production image under 250MB with non-root user and no dev deps.

**Files touched:**
| File | What gets built |
|---|---|
| `Dockerfile` | Multi-stage: builder (install deps) → runtime (copy venv only) |
| `.dockerignore` | Exclude `.git`, `tests/`, `__pycache__`, `.env` |

**Concepts covered:** Docker layer cache ordering, why `COPY pyproject.toml` comes before `COPY app/`, non-root container users, image size impact of dev dependencies.

**Checkpoint:** `docker images` shows image under 250MB. Container runs as non-root user.

---

#### Block 9 — Deploy to the Internet
**Goal:** Live URL that anyone can hit.

**Option A (Easiest):** FastAPI on Railway/Fly.io + local Ollama tunneled via `cloudflared`.
**Option B (Best):** Full stack on a Hetzner/DigitalOcean VPS via `docker compose`.
**Option C (Most impressive):** Kubernetes on DigitalOcean — Deployment + StatefulSet + Ingress + cert-manager.

**Files touched (Option B/C):**
| File | What gets built |
|---|---|
| `k8s/deployment.yaml` | FastAPI Deployment, 2 replicas |
| `k8s/ollama-statefulset.yaml` | Ollama StatefulSet with PVC for model storage |
| `k8s/service.yaml` | ClusterIP for app, LoadBalancer for ingress |
| `k8s/ingress.yaml` | nginx ingress + cert-manager TLS annotation |

**Checkpoint:** `curl https://your-domain/health` → 200 from the live server.

---

#### Block 10 — CI/CD + Final Polish
**Goal:** Green badge on README. Automated test → build → deploy on every push to main.

**Files touched:**
| File | What gets built |
|---|---|
| `.github/workflows/ci.yml` | pytest → docker build → push to GHCR → deploy |
| `examples/` | curl commands, sample requests/responses |
| `README.md` | Architecture diagram, setup instructions, live demo link, "what's next" section |

**Checkpoint:** Push to main → GitHub Actions goes green → image appears in GHCR → live server updates.

---

## What "Done" Looks Like

- Self-hosted LLM inference (no API keys, no costs)
- Vector search over your own documents
- Streaming responses over SSE
- API key auth with timing-attack-safe comparison
- Structured JSON logs with per-request trace IDs
- Prometheus metrics + Grafana dashboard
- Sub-250MB production Docker image
- Live deployment with HTTPS
- CI/CD pipeline with automated tests
- Clean GitHub repo a recruiter can read in 5 minutes

---

## Production Considerations (Intentionally Left Out)

These are real next steps — knowing what's missing matters as much as what's built:

- **Response caching** with Redis (same question shouldn't hit the LLM twice)
- **Background ingestion** with a job queue (Celery / ARQ) for large files
- **Query rewriting** — rephrase the user's question before embedding for better retrieval
- **Hybrid search** — combine BM25 keyword search with vector search (reciprocal rank fusion)
- **Evaluation pipeline** with `ragas` — measure retrieval precision and answer faithfulness
- **Guardrails** — detect and reject prompt injection attempts
- **Conversation memory** — store and summarize prior turns, not just the current message


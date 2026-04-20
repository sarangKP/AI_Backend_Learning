# rag_service/Dockerfile

# ── Stage 1: Builder ─────────────────────────────────────────
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies directly
RUN uv pip install --system --no-cache \
    fastapi "uvicorn[standard]" httpx \
    pydantic-settings "sqlalchemy[asyncio]" asyncpg \
    python-multipart structlog slowapi \
    prometheus-fastapi-instrumentator


# ── Stage 2: Runtime ─────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Create a non-root user — never run as root in production
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser

WORKDIR /app

# Copy installed packages from builder stage only
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Copy application code
COPY app/ ./app/

# Switch to non-root user
USER appuser

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
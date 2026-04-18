# rag_service/Dockerfile

FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first (for cache efficiency)
COPY pyproject.toml .
RUN uv pip install --system --no-cache -r pyproject.toml 2>/dev/null || \
    uv pip install --system --no-cache fastapi uvicorn[standard] \
    httpx pydantic-settings sqlalchemy[asyncio] asyncpg python-multipart

# Copy application code
COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
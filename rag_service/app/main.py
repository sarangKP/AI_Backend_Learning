# rag_service/app/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator
from app.routers import health, chat, documents
from app.config import get_settings
from app.auth import verify_api_key
from app.logging_config import setup_logging
from app.middleware import RequestTracingMiddleware

limiter = Limiter(key_func=get_remote_address)


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(debug=settings.debug)

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )

    # Middleware
    app.add_middleware(RequestTracingMiddleware)

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Prometheus metrics
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    # Routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(
        chat.router,
        prefix="/api/v1",
        tags=["chat"],
        dependencies=[Depends(verify_api_key)],
    )
    app.include_router(
        documents.router,
        prefix="/api/v1",
        tags=["documents"],
        dependencies=[Depends(verify_api_key)],
    )

    return app


app = create_app()
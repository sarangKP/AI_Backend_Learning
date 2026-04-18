# rag_service/app/main.py

from fastapi import FastAPI
from app.routers import health
from app.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )

    app.include_router(health.router, prefix="/api/v1", tags=["health"])

    return app


app = create_app()
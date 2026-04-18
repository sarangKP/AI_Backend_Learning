# rag_service/app/routers/health.py

from fastapi import APIRouter, Depends
from app.config import get_settings, Settings
from app.models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        debug=settings.debug,
    )
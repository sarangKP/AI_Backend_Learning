from fastapi import APIRouter

from app.config import settings
from app.db import check_db_connection
from app.models import EchoRequest, EchoResponse, HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    db_ok = await check_db_connection()
    return HealthResponse(
        status="ok" if db_ok else "degraded",
        service=settings.app_name,
    )


@router.post("/echo", response_model=EchoResponse)
async def echo(body: EchoRequest):
    return EchoResponse(message=body.message)

# rag_service/app/auth.py

import secrets
from fastapi import Header, HTTPException, status


async def verify_api_key(x_api_key: str = Header(...)) -> str:
    from app.config import get_settings
    settings = get_settings()

    is_valid = secrets.compare_digest(
        x_api_key.encode(),
        settings.api_key.encode(),
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

    return x_api_key
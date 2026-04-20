# rag_service/app/db.py

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config import get_settings

settings = get_settings()

database_url = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://"
)

engine = create_async_engine(
    database_url,
    echo=settings.debug,
)

AsyncSessionFactory = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    async with AsyncSessionFactory() as session:
        yield session
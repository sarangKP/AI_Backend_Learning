# rag_service/tests/conftest.py

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from app.main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture(autouse=True)
def mock_db(app):
    from unittest.mock import MagicMock

    mock_result = MagicMock()
    mock_result.fetchall.return_value = []  # fetchall() returns a plain empty list

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()

    async def override_get_db():
        yield mock_session

    from app.db import get_db
    app.dependency_overrides[get_db] = override_get_db
    yield mock_session
    app.dependency_overrides.clear()
# rag_service/tests/test_health.py

import pytest


@pytest.mark.anyio
async def test_health_returns_200(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_health_returns_correct_fields(client):
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["status"] == "ok"
    assert "app_name" in data
    assert "debug" in data
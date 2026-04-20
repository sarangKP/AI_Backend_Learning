# rag_service/tests/test_documents.py

import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.anyio
async def test_ingest_document(client):
    fake_embedding = [0.1] * 768

    with patch(
        "app.services.retrieval.embed_text",
        new=AsyncMock(return_value=fake_embedding),
    ):
        response = await client.post(
            "/api/v1/documents",
            json={
                "content": "Test document content",
                "source": "test-source",
            },
            headers={"X-Api-Key": "change-me-before-deploying"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["chunks_stored"] >= 1
    assert data["source"] == "test-source"
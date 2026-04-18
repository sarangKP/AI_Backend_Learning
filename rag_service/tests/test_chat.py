# rag_service/tests/test_chat.py

import pytest
from unittest.mock import patch, AsyncMock


async def fake_chat_stream(*args, **kwargs):
    import json
    tokens = ["Hello", " world", "!"]
    for token in tokens:
        yield json.dumps({"message": {"role": "assistant", "content": token}})


@pytest.mark.anyio
async def test_chat_streams_response(client):
    fake_embedding = [0.1] * 768

    with patch(
        "app.services.retrieval.embed_text",
        new=AsyncMock(return_value=fake_embedding),
    ), patch(
        "app.routers.chat.client.chat",
        new=fake_chat_stream,
    ):
        response = await client.post(
            "/api/v1/chat",
            json={"message": "Hello"},
        )

    assert response.status_code == 200
    assert "data:" in response.text
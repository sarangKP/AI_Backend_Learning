# rag_service/app/routers/chat.py

import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import ChatRequest
from app.services.ollama_client import OllamaClient
from app.services.retrieval import retrieve_similar

router = APIRouter()
client = OllamaClient()


async def stream_tokens(message: str, db: AsyncSession):
    # Step 1 — find relevant chunks from the database
    chunks = await retrieve_similar(query=message, db=db)

    # Step 2 — build context from retrieved chunks
    context = "\n\n".join(
        f"Source: {c['source']}\n{c['content']}" for c in chunks
    )

    # Step 3 — build messages with context injected
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. "
                "Use the following context to answer the user's question.\n\n"
                f"{context}"
            ),
        },
        {
            "role": "user",
            "content": message,
        },
    ]

    # Step 4 — stream the LLM response
    async for line in client.chat(messages):
        chunk = json.loads(line)
        token = chunk.get("message", {}).get("content", "")
        if token:
            yield f"data: {token}\n\n"




@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    return StreamingResponse(
        stream_tokens(request.message, db),
        media_type="text/event-stream",
    )
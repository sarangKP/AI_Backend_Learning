# rag_service/app/services/embeddings.py

from app.services.ollama_client import OllamaClient

_client = OllamaClient()


async def embed_text(text: str) -> list[float]:
    return await _client.embed(text)
# rag_service/app/services/ollama_client.py

import httpx
from app.config import get_settings

settings = get_settings()


class OllamaClient:
    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url
        self.chat_model = settings.ollama_chat_model
        self.embedding_model = settings.ollama_embedding_model

    async def embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.embedding_model,
                    "prompt": text,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()["embedding"]
        

    async def chat(
        self, messages: list[dict]
    ):
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={
                    "model": self.chat_model,
                    "messages": messages,
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        yield line
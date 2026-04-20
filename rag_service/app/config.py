# Updated rag_service/app/config.py

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "RAG Service"
    debug: bool = False

    database_url: str
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.2:3b"
    ollama_embedding_model: str = "nomic-embed-text"

    api_key: str = "change-me-before-deploying"

    allowed_origins: list[str] = ["http://localhost:3000"]
    rate_limit_per_minute: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()
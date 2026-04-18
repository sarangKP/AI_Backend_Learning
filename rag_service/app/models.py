# rag_service/app/models.py

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app_name: str
    debug: bool


class EchoRequest(BaseModel):
    message: str


class EchoResponse(BaseModel):
    echo: str


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class IngestRequest(BaseModel):
    content: str
    source: str = "unknown"


class IngestResponse(BaseModel):
    chunks_stored: int
    source: str


class SourceChunk(BaseModel):
    content: str
    source: str
from pydantic import BaseModel


# --- Request schemas ---

class EchoRequest(BaseModel):
    message: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class IngestRequest(BaseModel):
    content: str
    metadata: dict = {}


# --- Response schemas ---

class EchoResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str


class IngestResponse(BaseModel):
    chunks_stored: int


class SourceChunk(BaseModel):
    content: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]

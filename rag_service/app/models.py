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
# rag_service/app/routers/documents.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models import IngestRequest, IngestResponse
from app.services.retrieval import ingest_chunks

router = APIRouter()


@router.post("/documents", response_model=IngestResponse)
async def ingest_document(
    request: IngestRequest,
    db: AsyncSession = Depends(get_db),
) -> IngestResponse:
    chunks_stored = await ingest_chunks(
        content=request.content,
        source=request.source,
        db=db,
    )
    return IngestResponse(
        chunks_stored=chunks_stored,
        source=request.source,
    )
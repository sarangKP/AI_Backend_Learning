# rag_service/app/services/retrieval.py

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.embeddings import embed_text


def chunk_text(content: str, chunk_size: int = 500) -> list[str]:
    words = content.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
    return chunks


async def ingest_chunks(
    content: str,
    source: str,
    db: AsyncSession,
) -> int:
    chunks = chunk_text(content)
    for chunk in chunks:
        embedding = await embed_text(chunk)
        await db.execute(
            text(
                "INSERT INTO documents (content, embedding, source) "
                "VALUES (:content, :embedding, :source)"
            ),
            {
                "content": chunk,
                "embedding": str(embedding),
                "source": source,
            },
        )
    await db.commit()
    return len(chunks)


async def retrieve_similar(
    query: str,
    db: AsyncSession,
    top_k: int = 3,
) -> list[dict]:
    query_embedding = await embed_text(query)
    result = await db.execute(
        text(
            "SELECT content, source "
            "FROM documents "
            "ORDER BY embedding <=> :embedding "
            "LIMIT :top_k"
        ),
        {
            "embedding": str(query_embedding),
            "top_k": top_k,
        },
    )
    rows = result.fetchall()
    return [{"content": row[0], "source": row[1]} for row in rows]
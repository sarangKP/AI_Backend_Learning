-- rag_service/db/init.sql

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Store document chunks + their embeddings
CREATE TABLE IF NOT EXISTS documents (
    id        BIGSERIAL PRIMARY KEY,
    content   TEXT NOT NULL,
    embedding vector(768) NOT NULL,
    source    TEXT
);

-- Speed up similarity searches
CREATE INDEX IF NOT EXISTS documents_embedding_idx
    ON documents
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
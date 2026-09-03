from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.rag.ingestion.pipeline import MarkdownIngestionPipeline
from app.rag.models import DocumentInput, KnowledgeCategory
from app.rag.splitter import SemanticTextSplitter


class FakeEmbedding:
    async def embed_documents(self, texts):
        self.texts = texts
        return [[float(i), 1.0] for i, _ in enumerate(texts)]


@pytest.mark.asyncio
async def test_ingest_creates_document_chunks_and_vectors(monkeypatch):
    repo = AsyncMock()
    repo.create_document.return_value = 123
    repo.create_chunk.side_effect = [1001, 1002]
    repo.session = AsyncMock()

    monkeypatch.setattr(
        "app.rag.ingestion.pipeline.KnowledgeRepository",
        lambda session: repo,
    )

    vector_store = AsyncMock()
    embedding = FakeEmbedding()
    splitter = SemanticTextSplitter(chunk_size=20, overlap=3)
    pipeline = MarkdownIngestionPipeline(
        session=repo.session,
        embedding=embedding,
        vector_store=vector_store,
        splitter=splitter,
    )

    document = DocumentInput(
        title="ROE 规则",
        content="ROE 是衡量股东权益收益能力的指标。\n\nROE 越高通常表示资本使用效率更高。",
        category=KnowledgeCategory.FINANCIAL,
        source_type="MANUAL",
        metadata={"topic": "valuation"},
    )

    result = await pipeline.ingest(document)

    assert result == 123
    repo.create_document.assert_awaited_once()
    assert repo.create_chunk.await_count >= 1
    assert vector_store.upsert.await_count == repo.create_chunk.await_count
    repo.session.commit.assert_awaited_once()
    assert len(embedding.texts) == repo.create_chunk.await_count


@pytest.mark.asyncio
async def test_ingest_rejects_empty_document(monkeypatch):
    repo = AsyncMock()
    monkeypatch.setattr(
        "app.rag.ingestion.pipeline.KnowledgeRepository",
        lambda session: repo,
    )
    pipeline = MarkdownIngestionPipeline(
        session=repo,
        embedding=AsyncMock(),
        vector_store=AsyncMock(),
        splitter=SemanticTextSplitter(),
    )

    document = DocumentInput(
        title="empty",
        content="  \n\n ",
        category=KnowledgeCategory.MARKET,
    )

    with pytest.raises(ValueError, match="document content is empty"):
        await pipeline.ingest(document)

    repo.create_document.assert_not_awaited()

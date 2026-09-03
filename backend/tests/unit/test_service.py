from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.rag.context_builder import ContextBuilder
from app.rag.models import KnowledgeCategory
from app.rag.service import RagService
from app.rag.vector_store.base import VectorHit


class FakeEmbedding:
    async def embed_query(self, text):
        self.last_query = text
        return [0.1, 0.2]


class FakeQueryRewriter:
    def __init__(self, rewritten="贵州茅台 ROE 盈利能力 分析规则"):
        self.rewritten = rewritten
        self.calls = []

    async def rewrite(self, query):
        self.calls.append(query)
        return self.rewritten


class FakeReranker:
    def __init__(self, indexes):
        self.indexes = indexes
        self.calls = []

    async def rerank(self, query, documents):
        self.calls.append((query, documents))
        return [SimpleNamespace(index=i, score=1.0 - n * 0.1) for n, i in enumerate(self.indexes)]


@pytest.fixture
def service():
    repository = AsyncMock()
    vector_store = AsyncMock()
    embedding = FakeEmbedding()
    rewriter = FakeQueryRewriter()
    reranker = FakeReranker([1, 0])
    return RagService(
        repository=repository,
        vector_store=vector_store,
        embedding=embedding,
        reranker=reranker,
        query_rewriter=rewriter,
        context_builder=ContextBuilder(),
        vector_top_k=10,
        rerank_top_k=5,
    )


@pytest.mark.asyncio
async def test_retrieve_pipeline_query_rewrite_embedding_vector_search_hydration_rerank(service):
    service.vector_store.search.return_value = [
        VectorHit(chunk_id=1, document_id=100, score=0.90, metadata={}),
        VectorHit(chunk_id=2, document_id=100, score=0.80, metadata={}),
    ]
    service.repository.get_chunks.return_value = [
        SimpleNamespace(id=1, document_id=100, content="ROE 定义", metadata={"section": "roe"}),
        SimpleNamespace(id=2, document_id=100, content="现金流定义", metadata={}),
    ]
    service.repository.get_documents.return_value = {
        100: SimpleNamespace(
            id=100,
            title="财务指标规则",
            category="FINANCIAL",
            source_type="MANUAL",
            source_url=None,
            version="1.0",
        )
    }

    result = await service.retrieve("茅台盈利能力怎么看", category=KnowledgeCategory.FINANCIAL, top_k=2)

    assert len(result) == 2
    assert result[0].chunk_id == 2  # reranker reversed the vector candidates
    assert result[1].chunk_id == 1
    assert service.embedding.last_query == "贵州茅台 ROE 盈利能力 分析规则"
    service.vector_store.search.assert_awaited_once_with(
        vector=[0.1, 0.2], top_k=10, category="FINANCIAL"
    )
    assert service.repository.get_chunks.await_count == 1
    assert service.repository.get_documents.await_count == 1


@pytest.mark.asyncio
async def test_retrieve_returns_empty_when_vector_store_has_no_hits(service):
    service.vector_store.search.return_value = []
    result = await service.retrieve("ROE 是什么")
    assert result == []
    service.repository.get_chunks.assert_not_awaited()
    service.repository.get_documents.assert_not_awaited()


@pytest.mark.asyncio
async def test_retrieve_skips_orphaned_vector_hits(service):
    service.vector_store.search.return_value = [
        VectorHit(chunk_id=999, document_id=100, score=0.9, metadata={}),
    ]
    service.repository.get_chunks.return_value = []
    service.repository.get_documents.return_value = {}

    result = await service.retrieve("ROE")
    assert result == []
    service.reranker = AsyncMock()
    service.reranker.rerank.assert_not_awaited()


@pytest.mark.asyncio
async def test_retrieve_compliance_always_filters_compliance_category(service):
    service.vector_store.search.return_value = []

    await service.retrieve_compliance("我可以买入这只股票吗", top_k=3)

    service.vector_store.search.assert_awaited_once_with(
        vector=[0.1, 0.2], top_k=10, category="COMPLIANCE"
    )

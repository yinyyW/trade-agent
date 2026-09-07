from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

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
        return [
            SimpleNamespace(index=i, score=1.0 - n * 0.1)
            for n, i in enumerate(self.indexes)
        ]


@pytest.fixture
def parts(monkeypatch):
    repository = AsyncMock()
    session = AsyncMock()
    session_factory = Mock(return_value=session)

    monkeypatch.setattr(
        "app.rag.service.KnowledgeRepository",
        lambda _session: repository,
    )

    rag_service = RagService(
        session_factory=session_factory,
        vector_store=AsyncMock(),
        embedding=FakeEmbedding(),
        reranker=FakeReranker([1, 0]),
        query_rewriter=FakeQueryRewriter(),
        context_builder=ContextBuilder(),
        vector_top_k=10,
        rerank_top_k=5,
    )

    return SimpleNamespace(
        service=rag_service,
        repository=repository,
        session=session,
        session_factory=session_factory,
    )


@pytest.mark.asyncio
async def test_retrieve_pipeline_query_rewrite_embedding_vector_search_hydration_rerank(parts):
    parts.service.vector_store.search.return_value = [
        VectorHit(chunk_id=1, document_id=100, score=0.90, metadata={}),
        VectorHit(chunk_id=2, document_id=100, score=0.80, metadata={}),
    ]
    parts.repository.get_chunks.return_value = [
        SimpleNamespace(
            id=1,
            document_id=100,
            content="ROE 定义",
            extra_metadata={"section": "roe"},
        ),
        SimpleNamespace(
            id=2,
            document_id=100,
            content="现金流定义",
            extra_metadata={},
        ),
    ]
    parts.repository.get_documents.return_value = {
        100: SimpleNamespace(
            id=100,
            title="财务指标规则",
            category="FINANCIAL",
            source_type="MANUAL",
            source_url=None,
            version="1.0",
        )
    }

    result = await parts.service.retrieve(
        "茅台盈利能力怎么看",
        category=KnowledgeCategory.FINANCIAL,
        top_k=2,
    )

    assert len(result) == 2
    assert result[0].chunk_id == 2  # reranker reversed the vector candidates
    assert result[1].chunk_id == 1
    assert parts.service.embedding.last_query == "贵州茅台 ROE 盈利能力 分析规则"
    parts.service.vector_store.search.assert_awaited_once_with(
        vector=[0.1, 0.2], top_k=10, category="FINANCIAL"
    )
    parts.repository.get_chunks.assert_awaited_once()
    parts.repository.get_documents.assert_awaited_once()
    parts.session.commit.assert_awaited_once()
    parts.session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_retrieve_returns_empty_when_vector_store_has_no_hits(parts):
    parts.service.vector_store.search.return_value = []

    result = await parts.service.retrieve("ROE 是什么")

    assert result == []
    parts.repository.get_chunks.assert_not_awaited()
    parts.repository.get_documents.assert_not_awaited()
    parts.session_factory.assert_not_called()


@pytest.mark.asyncio
async def test_retrieve_skips_orphaned_vector_hits(parts):
    parts.service.vector_store.search.return_value = [
        VectorHit(chunk_id=999, document_id=100, score=0.9, metadata={}),
    ]
    parts.repository.get_chunks.return_value = []
    parts.repository.get_documents.return_value = {}

    result = await parts.service.retrieve("ROE")

    assert result == []
    parts.service.reranker = AsyncMock()
    parts.service.reranker.rerank.assert_not_awaited()


@pytest.mark.asyncio
async def test_retrieve_compliance_always_filters_compliance_category(parts):
    parts.service.vector_store.search.return_value = []

    await parts.service.retrieve_compliance("我可以买入这只股票吗", top_k=3)

    parts.service.vector_store.search.assert_awaited_once_with(
        vector=[0.1, 0.2], top_k=10, category="COMPLIANCE"
    )

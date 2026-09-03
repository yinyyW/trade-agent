import pytest

from app.rag.reranker import NoopReranker


@pytest.mark.asyncio
async def test_noop_reranker_preserves_vector_order():
    reranker = NoopReranker()
    result = await reranker.rerank("ROE 怎么看", ["doc-a", "doc-b", "doc-c"])
    assert [item.index for item in result] == [0, 1, 2]
    assert [item.score for item in result] == [0.0, 0.0, 0.0]


@pytest.mark.asyncio
async def test_noop_reranker_empty_documents():
    result = await NoopReranker().rerank("query", [])
    assert result == []

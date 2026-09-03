import hashlib
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.rag.repository import KnowledgeRepository


@pytest.mark.asyncio
async def test_create_document_flushes_and_returns_generated_id():
    session = Mock()
    session.flush = AsyncMock()

    def add(obj):
        obj.id = 101

    session.add.side_effect = add
    repo = KnowledgeRepository(session)

    result = await repo.create_document(
        title="财务指标释义",
        category="FINANCIAL",
        source_type="MANUAL",
        content="ROE 内容",
        source_url=None,
        author="test",
        version="1.0",
    )

    assert result == 101
    session.add.assert_called_once()
    session.flush.assert_awaited_once()
    obj = session.add.call_args.args[0]
    assert obj.title == "财务指标释义"
    assert obj.category == "FINANCIAL"
    assert obj.status == "ACTIVE"


@pytest.mark.asyncio
async def test_create_chunk_calculates_sha256_hash():
    session = Mock()
    session.flush = AsyncMock()

    def add(obj):
        obj.id = 1001

    session.add.side_effect = add
    repo = KnowledgeRepository(session)
    content = "ROE 是衡量股东权益收益能力的指标。"

    result = await repo.create_chunk(
        document_id=101,
        chunk_index=0,
        content=content,
        token_count=len(content),
        metadata={"section": "roe"},
    )

    assert result == 1001
    obj = session.add.call_args.args[0]
    assert obj.content_hash == hashlib.sha256(content.encode("utf-8")).hexdigest()
    assert obj.document_id == 101
    assert obj.chunk_index == 0
    assert obj.extra_metadata == {"section": "roe"}


@pytest.mark.asyncio
async def test_get_chunks_and_documents_return_expected_shapes():
    session = AsyncMock()
    repo = KnowledgeRepository(session)

    chunk = SimpleNamespace(id=1, document_id=10)
    document = SimpleNamespace(id=10, title="ROE")

    chunk_result = SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [chunk]))
    doc_result = SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [document]))
    session.execute.side_effect = [chunk_result, doc_result]

    chunks = await repo.get_chunks([1])
    docs = await repo.get_documents([10])

    assert chunks == [chunk]
    assert docs == {10: document}
    assert session.execute.await_count == 2


@pytest.mark.asyncio
async def test_empty_ids_return_empty_without_database_call():
    session = AsyncMock()
    repo = KnowledgeRepository(session)

    assert await repo.get_chunks([]) == []
    assert await repo.get_documents([]) == {}
    session.execute.assert_not_awaited()

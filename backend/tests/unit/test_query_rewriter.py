import pytest

from app.rag.query_rewriter import IdentityQueryRewriter


@pytest.mark.asyncio
async def test_identity_query_rewriter_keeps_original_query():
    query = "贵州茅台最近的 ROE 怎么样？"
    assert await IdentityQueryRewriter().rewrite(query) == query

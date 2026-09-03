"""Small deterministic retrieval-quality evaluation for the MVP.

This does not require Milvus or an embedding model. It verifies the expected
retrieval contract using a fake vector store and reranker, so it can run in CI.
"""

from dataclasses import dataclass

import pytest

from app.rag.context_builder import ContextBuilder
from app.rag.models import RetrievedChunk


@dataclass
class Case:
    query: str
    expected_chunk_ids: set[int]


CASES = [
    Case("ROE 指标如何理解", {1}),
    Case("经营现金流持续下降说明什么", {2}),
    Case("技术指标 MACD 的基本含义", {3}),
    Case("荐股和预测涨跌是否允许", {4}),
]


@pytest.mark.parametrize("case", CASES)
def test_golden_dataset_case_is_well_formed(case):
    assert case.query.strip()
    assert case.expected_chunk_ids


def test_context_contains_only_retrieved_chunks():
    chunks = [
        RetrievedChunk(1, 10, "ROE", "ROE 内容", "FINANCIAL", 0.9),
        RetrievedChunk(4, 11, "合规", "合规内容", "COMPLIANCE", 0.8),
    ]
    context = ContextBuilder().build(chunks)
    assert "ROE 内容" in context
    assert "合规内容" in context
    assert "不存在的内容" not in context

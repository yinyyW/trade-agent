from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class KnowledgeCategory(str, Enum):
    FINANCIAL = "FINANCIAL"
    MACRO = "MACRO"
    MARKET = "MARKET"
    TECHNICAL = "TECHNICAL"
    COMPLIANCE = "COMPLIANCE"
    ANALYZE = "ANALYZE"


@dataclass(slots=True)
class DocumentInput:
    title: str
    content: str
    category: KnowledgeCategory
    source_type: str = "MANUAL"
    source_url: str | None = None
    author: str | None = None
    version: str = "1.0"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ChunkInput:
    document_id: int
    chunk_index: int
    content: str
    token_count: int
    content_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RetrievedChunk:
    chunk_id: int
    document_id: int
    title: str
    content: str
    category: str
    vector_score: float
    rerank_score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class VectorHit:
    chunk_id: int
    document_id: int
    score: float
    metadata: dict[str, Any]


class VectorStore(ABC):
    @abstractmethod
    async def ensure_collection(self, dimension: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def upsert(
        self,
        chunk_id: int,
        document_id: int,
        vector: list[float],
        metadata: dict[str, Any],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def search(
        self,
        vector: list[float],
        top_k: int,
        category: str | None = None,
    ) -> list[VectorHit]:
        raise NotImplementedError

    @abstractmethod
    async def delete_by_chunk_ids(self, chunk_ids: list[int]) -> None:
        raise NotImplementedError

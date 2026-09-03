from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class RerankItem:
    index: int
    score: float


class Reranker(ABC):
    @abstractmethod
    async def rerank(self, query: str, documents: list[str]) -> list[RerankItem]:
        raise NotImplementedError


class NoopReranker(Reranker):
    async def rerank(self, query: str, documents: list[str]) -> list[RerankItem]:
        # Keep vector-search order.
        return [RerankItem(index=i, score=0.0) for i in range(len(documents))]


class CrossEncoderReranker(Reranker):
    def __init__(self, model_name: str):
        from sentence_transformers import CrossEncoder

        self._model = CrossEncoder(model_name)

    def _predict(self, pairs: list[tuple[str, str]]) -> list[float]:
        return [float(x) for x in self._model.predict(pairs)]

    async def rerank(self, query: str, documents: list[str]) -> list[RerankItem]:
        pairs = [(query, doc) for doc in documents]
        scores = await asyncio.to_thread(self._predict, pairs)
        ranked = sorted(
            (RerankItem(index=i, score=s) for i, s in enumerate(scores)),
            key=lambda x: x.score,
            reverse=True,
        )
        return ranked

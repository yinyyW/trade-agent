from __future__ import annotations

import asyncio
import json
from typing import Any

from .base import VectorHit, VectorStore


class MilvusVectorStore(VectorStore):
    def __init__(self, uri: str, collection_name: str):
        from pymilvus import MilvusClient

        self.client = MilvusClient(uri=uri)
        self.collection_name = collection_name

    async def ensure_collection(self, dimension: int) -> None:
        await asyncio.to_thread(self._ensure_collection, dimension)

    def _ensure_collection(self, dimension: int) -> None:
        from pymilvus import DataType

        if self.client.has_collection(self.collection_name):
            return

        schema = self.client.create_schema(
            auto_id=False,
            enable_dynamic_field=False,
        )
        schema.add_field("id", DataType.INT64, is_primary=True)
        schema.add_field("document_id", DataType.INT64)
        schema.add_field("category", DataType.VARCHAR, max_length=32)
        schema.add_field("metadata", DataType.VARCHAR, max_length=4096)
        schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=dimension)

        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="embedding",
            index_type="AUTOINDEX",
            metric_type="COSINE",
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params,
        )

    async def upsert(
        self,
        chunk_id: int,
        document_id: int,
        vector: list[float],
        metadata: dict[str, Any],
    ) -> None:
        row = {
            "id": chunk_id,
            "document_id": document_id,
            "category": str(metadata.get("category", "")),
            "metadata": json.dumps(metadata, ensure_ascii=False),
            "embedding": vector,
        }
        await asyncio.to_thread(
            self.client.upsert,
            collection_name=self.collection_name,
            data=[row],
        )

    async def search(
        self,
        vector: list[float],
        top_k: int,
        category: str | None = None,
    ) -> list[VectorHit]:
        expr = None
        if category:
            escaped = category.replace("\\", "\\\\").replace('"', '\\"')
            expr = f'category == "{escaped}"'

        result = await asyncio.to_thread(
            self.client.search,
            collection_name=self.collection_name,
            data=[vector],
            anns_field="embedding",
            limit=top_k,
            filter=expr,
            output_fields=["document_id", "category", "metadata"],
            search_params={"metric_type": "COSINE"},
        )

        hits: list[VectorHit] = []
        for item in result[0]:
            raw_metadata = item.get("entity", {}).get("metadata", "{}")
            try:
                metadata = json.loads(raw_metadata)
            except json.JSONDecodeError:
                metadata = {}

            hits.append(
                VectorHit(
                    chunk_id=int(item["id"]),
                    document_id=int(item["entity"]["document_id"]),
                    score=float(item["distance"]),
                    metadata=metadata,
                )
            )
        return hits

    async def delete_by_chunk_ids(self, chunk_ids: list[int]) -> None:
        if not chunk_ids:
            return
        expr = f"id in [{','.join(str(i) for i in chunk_ids)}]"
        await asyncio.to_thread(
            self.client.delete,
            collection_name=self.collection_name,
            filter=expr,
        )

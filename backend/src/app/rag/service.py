from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .context_builder import ContextBuilder
from .embedding.base import EmbeddingModel
from .models import KnowledgeCategory, RetrievedChunk
from .query_rewriter import QueryRewriter
from .reranker import Reranker
from .repository import KnowledgeRepository
from .vector_store.base import VectorStore

class RagService:

    def __init__(
        self,
        *,
        session_factory: async_sessionmaker[AsyncSession],
        vector_store: VectorStore,
        embedding: EmbeddingModel,
        reranker: Reranker,
        query_rewriter: QueryRewriter,
        context_builder: ContextBuilder,
        vector_top_k: int = 10,
        rerank_top_k: int = 5,
    ):
        self.session_factory = session_factory
        self.vector_store = vector_store
        self.embedding = embedding
        self.reranker = reranker
        self.query_rewriter = query_rewriter
        self.context_builder = context_builder
        self.vector_top_k = vector_top_k
        self.rerank_top_k = rerank_top_k

    async def retrieve(
        self,
        query: str,
        *,
        category: KnowledgeCategory | str | None = None,
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:

        # 1. Query Rewrite
        rewritten = await self.query_rewriter.rewrite(query)

        # 2. Embedding
        vector = await self.embedding.embed_query(rewritten)

        category_value = (
            category.value
            if isinstance(category, KnowledgeCategory)
            else category
        )

        # 3. Vector Search
        hits = await self.vector_store.search(
            vector=vector,
            top_k=self.vector_top_k,
            category=category_value,
        )

        if not hits:
            return []

        chunk_ids = [x.chunk_id for x in hits]

        # 4. Load data from DB
        async with self.session_factory() as session:

            repository = KnowledgeRepository(session)

            chunks = await repository.get_chunks(chunk_ids)

            chunk_map = {
                x.id: x
                for x in chunks
            }

            doc_ids = list({
                x.document_id
                for x in chunks
            })

            documents = await repository.get_documents(
                doc_ids
            )

            candidates: list[RetrievedChunk] = []

            for hit in hits:

                chunk = chunk_map.get(hit.chunk_id)

                document = documents.get(
                    hit.document_id
                )

                if not chunk or not document:
                    continue

                candidates.append(
                    RetrievedChunk(
                        chunk_id=chunk.id,
                        document_id=document.id,
                        title=document.title,
                        content=chunk.content,
                        category=document.category,
                        vector_score=hit.score,
                        metadata={
                            **(chunk.extra_metadata or {}),
                            "source_type": document.source_type,
                            "source_url": document.source_url,
                            "version": document.version,
                        },
                    )
                )

        if not candidates:
            return []

        # 5. Rerank
        ranked = await self.reranker.rerank(
            rewritten,
            [x.content for x in candidates],
        )

        # 6. Build result
        limit = top_k or self.rerank_top_k

        result: list[RetrievedChunk] = []

        for item in ranked[:limit]:
            candidate = candidates[item.index]
            candidate.rerank_score = item.score
            result.append(candidate)

        return result

    async def retrieve_compliance(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:

        return await self.retrieve(
            query,
            category=KnowledgeCategory.COMPLIANCE,
            top_k=top_k,
        )

    def build_context(
        self,
        chunks: list[RetrievedChunk],
    ) -> str:

        return self.context_builder.build(chunks)
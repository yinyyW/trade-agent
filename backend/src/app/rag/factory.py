from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .context_builder import ContextBuilder
from .embedding.sentence_transformer import SentenceTransformerEmbedding
from .query_rewriter import (
    DeepSeekQueryRewriter,
    IdentityQueryRewriter,
)
from .reranker import CrossEncoderReranker, NoopReranker
from .repository import KnowledgeRepository
from .service import RagService
from .vector_store.milvus import MilvusVectorStore


def create_rag_service(session: AsyncSession) -> RagService:
    embedding = SentenceTransformerEmbedding(settings.embedding_model)

    vector_store = MilvusVectorStore(
        uri=settings.milvus_uri,
        collection_name=settings.milvus_collection,
    )

    if settings.reranker_model:
        reranker = CrossEncoderReranker(settings.reranker_model)
    else:
        reranker = NoopReranker()

    if settings.query_rewrite_enabled:
        if not settings.deepseek_api_key:
            raise ValueError(
                "RAG_QUERY_REWRITE_ENABLED=true requires RAG_DEEPSEEK_API_KEY"
            )
        query_rewriter = DeepSeekQueryRewriter(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            model=settings.deepseek_model,
        )
    else:
        query_rewriter = IdentityQueryRewriter()

    return RagService(
        repository=KnowledgeRepository(session),
        vector_store=vector_store,
        embedding=embedding,
        reranker=reranker,
        query_rewriter=query_rewriter,
        context_builder=ContextBuilder(),
        vector_top_k=settings.vector_top_k,
        rerank_top_k=settings.rerank_top_k,
    )

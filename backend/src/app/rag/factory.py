from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .config import rag_settings
from .context_builder import ContextBuilder
from .embedding.sentence_transformer import SentenceTransformerEmbedding
from .query_rewriter import (
    DeepSeekQueryRewriter,
    IdentityQueryRewriter,
)
from .reranker import CrossEncoderReranker, NoopReranker
from .service import RagService
from .vector_store.milvus import MilvusVectorStore


def create_rag_service(
    session_factory: async_sessionmaker[AsyncSession],
) -> RagService:
    embedding = SentenceTransformerEmbedding(rag_settings.embedding_model)

    vector_store = MilvusVectorStore(
        uri=rag_settings.milvus_uri,
        collection_name=rag_settings.milvus_collection,
    )

    if rag_settings.reranker_model:
        reranker = CrossEncoderReranker(rag_settings.reranker_model)
    else:
        reranker = NoopReranker()

    if rag_settings.query_rewrite_enabled:
        if not rag_settings.deepseek_api_key:
            raise ValueError(
                "RAG_QUERY_REWRITE_ENABLED=true requires RAG_DEEPSEEK_API_KEY"
            )
        query_rewriter = DeepSeekQueryRewriter(
            api_key=rag_settings.deepseek_api_key,
            base_url=rag_settings.deepseek_base_url,
            model=rag_settings.deepseek_model,
        )
    else:
        query_rewriter = IdentityQueryRewriter()

    return RagService(
        session_factory=session_factory,
        vector_store=vector_store,
        embedding=embedding,
        reranker=reranker,
        query_rewriter=query_rewriter,
        context_builder=ContextBuilder(),
        vector_top_k=rag_settings.vector_top_k,
        rerank_top_k=rag_settings.rerank_top_k,
    )

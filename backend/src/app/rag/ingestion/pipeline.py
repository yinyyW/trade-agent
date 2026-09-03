from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from ..embedding.base import EmbeddingModel
from ..models import DocumentInput
from ..repository import KnowledgeRepository
from ..splitter import SemanticTextSplitter
from ..vector_store.base import VectorStore


class MarkdownIngestionPipeline:
    def __init__(
        self,
        *,
        session: AsyncSession,
        embedding: EmbeddingModel,
        vector_store: VectorStore,
        splitter: SemanticTextSplitter,
    ):
        self.repo = KnowledgeRepository(session)
        self.embedding = embedding
        self.vector_store = vector_store
        self.splitter = splitter

    async def ingest(self, document: DocumentInput) -> int:
        # 1. 分割文档
        chunks = self.splitter.split(document.content)
        if not chunks:
            raise ValueError("document content is empty")

        # 2. 保存文档至数据库
        document_id = await self.repo.create_document(
            title=document.title,
            category=document.category.value,
            source_type=document.source_type,
            content=document.content,
            source_url=document.source_url,
            author=document.author,
            version=document.version,
        )

        # 3. 切割后的文档转化为向量
        vectors = await self.embedding.embed_documents(chunks)

        for index, (content, vector) in enumerate(zip(chunks, vectors)):
            # 4. 保存切割后的文档至数据库
            chunk_id = await self.repo.create_chunk(
                document_id=document_id,
                chunk_index=index,
                content=content,
                token_count=len(content),
                metadata={
                    **document.metadata,
                    "category": document.category.value,
                    "title": document.title,
                    "source_type": document.source_type,
                },
            )

            # 5. 保存向量
            await self.vector_store.upsert(
                chunk_id=chunk_id,
                document_id=document_id,
                vector=vector,
                metadata={
                    **document.metadata,
                    "category": document.category.value,
                    "title": document.title,
                    "source_type": document.source_type,
                },
            )

        await self.repo.session.commit()
        return document_id


def load_markdown(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")

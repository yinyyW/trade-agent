from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class KnowledgeDocumentORM(Base):
    __tablename__ = "knowledge_document"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(50), index=True)
    source_type: Mapped[str] = mapped_column(String(30))
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    author: Mapped[str | None] = mapped_column(String(100), nullable=True)
    version: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)


class KnowledgeChunkORM(Base):
    __tablename__ = "knowledge_chunk"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_document.id"), index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    token_count: Mapped[int] = mapped_column(Integer)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    vector_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)


class KnowledgeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_document(
        self,
        title: str,
        category: str,
        source_type: str,
        content: str,
        source_url: str | None,
        author: str | None,
        version: str,
    ) -> int:
        now = datetime.utcnow()
        obj = KnowledgeDocumentORM(
            title=title,
            category=category,
            source_type=source_type,
            content=content,
            source_url=source_url,
            author=author,
            version=version,
            status="ACTIVE",
            created_at=now,
            updated_at=now,
        )
        self.session.add(obj)
        await self.session.flush()
        return obj.id

    async def create_chunk(
        self,
        document_id: int,
        chunk_index: int,
        content: str,
        token_count: int,
        metadata: dict[str, Any],
    ) -> int:
        now = datetime.utcnow()
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        obj = KnowledgeChunkORM(
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            token_count=token_count,
            content_hash=content_hash,
            metadata=metadata,
            created_at=now,
            updated_at=now,
        )
        self.session.add(obj)
        await self.session.flush()
        return obj.id

    async def get_chunks(self, ids: list[int]) -> list[KnowledgeChunkORM]:
        if not ids:
            return []
        result = await self.session.execute(
            select(KnowledgeChunkORM).where(KnowledgeChunkORM.id.in_(ids))
        )
        return list(result.scalars().all())

    async def get_documents(
        self, ids: list[int]
    ) -> dict[int, KnowledgeDocumentORM]:
        if not ids:
            return {}
        result = await self.session.execute(
            select(KnowledgeDocumentORM).where(KnowledgeDocumentORM.id.in_(ids))
        )
        return {x.id: x for x in result.scalars().all()}

import asyncio

from app.rag.factory import create_rag_service
from app.rag.config import database_settings
from app.rag.models import KnowledgeCategory
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

def create_session_factory():
    database_url = getattr(database_settings, "database_url", None)

    if not database_url:
        raise RuntimeError(
            "未配置 database_url，请在 .env 中配置 DATABASE_URL"
        )

    engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
    )

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return engine, session_factory

async def test_rag_service():
    engine, session_factory = create_session_factory()
    query = "PPI 是什么？"

    try:
        rag_service = create_rag_service(session_factory=session_factory)
        result = await rag_service.retrieve(query=query, category=KnowledgeCategory.MACRO, top_k=3)
        print(f"result = {result}")
    finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_rag_service())

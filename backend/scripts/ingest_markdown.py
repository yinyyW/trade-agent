"""
Markdown 知识库导入脚本

单文件导入：

    python scripts/ingest_markdown.py \
        --file knowledge/technical/macd.md \
        --title "MACD 技术指标分析" \
        --category TECHNICAL

批量导入：

    python scripts/ingest_markdown.py \
        --dir knowledge/technical \
        --category TECHNICAL

说明：
    Markdown
        ↓
    SemanticTextSplitter
        ↓
    Embedding
        ↓
    MySQL + Milvus

MySQL：
    - knowledge_document
    - knowledge_chunk

Milvus：
    - chunk vector
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.rag.config import rag_settings, database_settings
from app.rag.embedding.sentence_transformer import SentenceTransformerEmbedding
from app.rag.ingestion.pipeline import (
    MarkdownIngestionPipeline,
    load_markdown,
)
from app.rag.models import DocumentInput, KnowledgeCategory
from app.rag.splitter import SemanticTextSplitter
from app.rag.vector_store.milvus import MilvusVectorStore


def create_session_factory():
    """
    创建 SQLAlchemy AsyncSession 工厂。

    需要在 settings 中配置：
        database_url

    示例：

        mysql+aiomysql://root:password@127.0.0.1:3306/ai_trading
    """

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


def build_pipeline(session: AsyncSession) -> MarkdownIngestionPipeline:
    """
    创建 MarkdownIngestionPipeline。
    """

    embedding = SentenceTransformerEmbedding(
        model_name=rag_settings.embedding_model,
    )

    vector_store = MilvusVectorStore(
        uri=rag_settings.milvus_uri,
        collection_name=rag_settings.milvus_collection
    )

    splitter = SemanticTextSplitter(
        chunk_size=rag_settings.chunk_size,
        overlap=rag_settings.chunk_overlap,
    )

    return MarkdownIngestionPipeline(
        session=session,
        embedding=embedding,
        vector_store=vector_store,
        splitter=splitter,
    )


async def ingest_file(
    session: AsyncSession,
    file_path: Path,
    category: KnowledgeCategory,
    title: str | None = None,
    doc_id: str | None = None,
) -> int:
    """
    导入单个 Markdown 文件。

    Args:
        session:
            SQLAlchemy AsyncSession

        file_path:
            Markdown 文件路径

        category:
            知识库分类

        title:
            文档标题，不传时默认使用文件名

        doc_id:
            外部业务文档 ID。
            当前 DocumentInput 没有 doc_id 字段，
            因此放入 metadata 中。
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"文件不存在：{file_path}"
        )

    if not file_path.is_file():
        raise ValueError(
            f"不是文件：{file_path}"
        )

    if file_path.suffix.lower() != ".md":
        raise ValueError(
            f"只支持 Markdown 文件：{file_path}"
        )

    content = load_markdown(file_path)

    if not content.strip():
        raise ValueError(
            f"Markdown 内容为空：{file_path}"
        )

    document_title = title or file_path.stem

    metadata = {
        "filename": file_path.name,
        "file_path": str(file_path),
    }

    if doc_id:
        metadata["doc_id"] = doc_id

    document = DocumentInput(
        title=document_title,
        content=content,
        category=category,
        source_type="MARKDOWN",
        source_url=None,
        author=None,
        version="1.0",
        metadata=metadata,
    )

    pipeline = build_pipeline(session)

    document_id = await pipeline.ingest(document)

    return document_id


async def ingest_directory(
    session: AsyncSession,
    directory: Path,
    category: KnowledgeCategory,
) -> None:
    """
    批量导入目录下所有 Markdown 文件。

    例如：

        knowledge/technical/
            macd.md
            ma.md
            rsi.md
            boll.md

    会全部导入。
    """

    if not directory.exists():
        raise FileNotFoundError(
            f"目录不存在：{directory}"
        )

    if not directory.is_dir():
        raise ValueError(
            f"不是目录：{directory}"
        )

    files = sorted(
        directory.rglob("*.md")
    )

    if not files:
        print(
            f"目录中没有找到 Markdown 文件：{directory}"
        )
        return

    print(
        f"发现 {len(files)} 个 Markdown 文件"
    )

    success_count = 0
    failed_count = 0

    for index, file_path in enumerate(files, start=1):
        print(
            f"\n[{index}/{len(files)}] "
            f"正在导入：{file_path}"
        )

        try:
            document_id = await ingest_file(
                session=session,
                file_path=file_path,
                category=category,
            )

            success_count += 1

            print(
                f"✓ 导入成功 "
                f"(document_id={document_id})"
            )

        except Exception as exc:
            failed_count += 1

            print(
                f"✗ 导入失败：{file_path}"
            )
            print(
                f"  错误：{exc}"
            )

            # 当前文件失败后回滚事务，
            # 避免影响后续文件。
            await session.rollback()

    print("\n" + "=" * 50)
    print("Markdown 导入完成")
    print("=" * 50)
    print(f"总文件数：{len(files)}")
    print(f"成功：{success_count}")
    print(f"失败：{failed_count}")


async def main():
    parser = argparse.ArgumentParser(
        description="将 Markdown 金融知识导入 RAG 知识库"
    )

    source_group = parser.add_mutually_exclusive_group(
        required=True
    )

    source_group.add_argument(
        "--file",
        type=Path,
        help="导入单个 Markdown 文件",
    )

    source_group.add_argument(
        "--dir",
        type=Path,
        help="批量导入 Markdown 目录",
    )

    parser.add_argument(
        "--title",
        type=str,
        help=(
            "文档标题，仅 --file 模式有效；"
            "不传时使用文件名"
        ),
    )

    parser.add_argument(
        "--doc-id",
        type=str,
        help=(
            "外部业务文档 ID，"
            "当前保存到 DocumentInput.metadata"
        ),
    )

    parser.add_argument(
        "--category",
        required=True,
        choices=[
            category.value
            for category in KnowledgeCategory
        ],
        help="知识库分类",
    )

    args = parser.parse_args()

    category = KnowledgeCategory(
        args.category
    )

    engine, session_factory = create_session_factory()

    try:
        async with session_factory() as session:

            # 单文件模式
            if args.file:

                document_id = await ingest_file(
                    session=session,
                    file_path=args.file,
                    category=category,
                    title=args.title,
                    doc_id=args.doc_id,
                )

                print("\n" + "=" * 50)
                print("Markdown 导入成功")
                print("=" * 50)
                print(f"文件：{args.file}")
                print(
                    f"标题："
                    f"{args.title or args.file.stem}"
                )
                print(
                    f"分类：{category.value}"
                )
                print(
                    f"document_id：{document_id}"
                )

            # 目录模式
            elif args.dir:

                await ingest_directory(
                    session=session,
                    directory=args.dir,
                    category=category,
                )

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

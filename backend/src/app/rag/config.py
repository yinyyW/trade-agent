from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class RagSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RAG_",
        env_file=Path(__file__).resolve().parents[3] / ".env",
        extra="ignore",
    )

    milvus_uri: str = "http://localhost:19530"
    milvus_collection: str = "rag_chunks"
    milvus_dim: int = 1024

    embedding_model: str = "BAAI/bge-m3"
    reranker_model: str | None = None

    chunk_size: int = 600
    chunk_overlap: int = 100

    vector_top_k: int = 10
    rerank_top_k: int = 5

    # Optional LLM-based query rewriting.
    query_rewrite_enabled: bool = False
    deepseek_api_key: str | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-v4-flash"

class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
            env_file=Path(__file__).resolve().parents[3] / ".env",
            extra="ignore",
        )
    database_url: str = ""

rag_settings = RagSettings()
database_settings = DatabaseSettings()

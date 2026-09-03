# RAG 测试说明

## 测试分层

- `unit/test_splitter.py`：文本切分边界、空文本、重叠窗口。
- `unit/test_reranker.py`：重排序器基础契约。
- `unit/test_context_builder.py`：上下文构造与提示注入防护。
- `unit/test_service.py`：Query Rewrite → Embedding → Vector Search → MySQL Hydration → Rerank 主链路。
- `unit/test_repository.py`：MySQL Repository 数据访问契约，使用 SQLite 内存库替代真实 MySQL。
- `unit/test_ingestion.py`：Markdown → Chunk → Embedding → MySQL → VectorStore 入库链路。
- `evaluation/test_retrieval_quality.py`：预留 Golden Dataset / 检索质量评估入口。

## 运行

```bash
pip install -r requirements-test.txt
pytest
```

## 真实基础设施测试

默认测试不连接真实 Milvus、MySQL、Embedding 模型和 DeepSeek，避免 CI 不稳定。
建议另外建立 `tests/integration/`，通过 Docker Compose 启动 MySQL + Milvus 后执行真实链路测试。

from __future__ import annotations

from langchain_core.messages import HumanMessage

from app.agent.state import AgentState
from app.rag.service import RagService


class RAGNode:

    def __init__(
        self,
        rag_service: RagService,
        *,
        top_k: int = 5,
    ):
        self.rag_service = rag_service
        self.top_k = top_k

    async def __call__(
        self,
        state: AgentState,
    ) -> dict:

        messages = state.get("messages", [])

        if not messages:
            return {
                "rag_context": [],
            }

        # 找到最后一条用户消息
        query = ""

        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                query = str(message.content)
                break

        if not query.strip():
            return {
                "rag_context": [],
            }

        results = await self.rag_service.retrieve(
            query,
            top_k=self.top_k,
        )

        context = []

        for item in results:
            context.append(
                {
                    "chunk_id": item.chunk_id,
                    "document_id": item.document_id,
                    "title": item.title,
                    "content": item.content,
                    "score": item.score,
                    "category": item.category,
                    "metadata": item.metadata,
                }
            )

        return {
            "rag_context": context,
        }
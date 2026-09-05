from __future__ import annotations

from langchain_core.messages import SystemMessage

from app.agent.context import format_rag_context
from app.agent.state import AgentState


SYSTEM_PROMPT = """
你是一个专业的金融 AI Agent。

你的主要职责：

1. 回答金融、证券、宏观经济、基金、债券、期货等问题。
2. 对实时、历史、财务、行情类数据，优先使用 MCP 工具获取真实数据。
3. 对金融概念、理论、分析方法，优先参考 RAG 知识库。
4. 如果问题同时需要知识和实时数据，可以同时使用 RAG 和 MCP。
5. 不要编造金融数据。
6. 如果工具没有返回相关数据，明确告诉用户。
7. 对数据进行分析时，需要区分：
   - 客观数据
   - 数据推导
   - 主观判断
8. 不构成投资建议。

回答尽量清晰、专业，并说明关键数据来源。
"""


class LLMNode:

    def __init__(self, llm):

        self.llm = llm

    async def __call__(
        self,
        state: AgentState,
    ) -> dict:

        rag_context = format_rag_context(
            state.get("rag_context", [])
        )

        system_prompt = (
            SYSTEM_PROMPT
            + "\n\n"
            + "以下是本轮 RAG 检索结果：\n"
            + rag_context
        )

        messages = state.get(
            "messages",
            [],
        )

        input_messages = [
            SystemMessage(
                content=system_prompt
            ),
            *messages,
        ]

        response = await self.llm.ainvoke(
            input_messages
        )

        return {
            "messages": [response],
        }
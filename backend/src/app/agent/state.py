from __future__ import annotations

from typing import Annotated, Any

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    """
    LangGraph Agent 全局状态。
    """

    # 对话消息
    messages: Annotated[list[BaseMessage], add_messages]

    # 用户信息
    user_id: int | None
    conversation_id: str

    # Agent 类型
    agent_type: str

    # RAG 检索结果
    rag_context: list[dict[str, Any]]

    # 是否需要 MCP
    need_tools: bool

    # MCP 调用记录
    tool_calls: list[dict[str, Any]]

    # 最终答案
    answer: str
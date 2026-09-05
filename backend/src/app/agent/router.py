from __future__ import annotations

from typing import Literal

from langchain_core.messages import AIMessage

from app.agent.state import AgentState


def route_after_llm(
    state: AgentState,
) -> Literal["mcp", "end"]:

    messages = state.get(
        "messages",
        [],
    )

    if not messages:
        return "end"

    last_message = messages[-1]

    if isinstance(last_message, AIMessage):

        tool_calls = getattr(
            last_message,
            "tool_calls",
            None,
        )

        if tool_calls:
            return "mcp"

    return "end"
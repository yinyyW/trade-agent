from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from app.agent.event_adapter import SSEEventAdapter
from app.agent.factory import AgentFactory


class AgentService:

    def __init__(
        self,
        *,
        factory: AgentFactory,
        event_adapter: SSEEventAdapter,
    ):
        self.factory = factory
        self.event_adapter = event_adapter

    async def stream(
        self,
        *,
        agent_type: str,
        messages: list,
        conversation_id: str,
        user_id: int | None = None,
    ) -> AsyncIterator:

        agent = self.factory.create(
            agent_type=agent_type,
        )

        events = agent.astream_events(
            {
                "messages": messages,
                "conversation_id": conversation_id,
                "user_id": user_id,
                "agent_type": agent_type,
                "rag_context": [],
                "tool_calls": [],
            },
            version="v2",
        )

        yield_event = True

        async for event in self.event_adapter.adapt(
            events
        ):
            if yield_event:
                yield event

        # 最终结束事件
        from app.agent.events import AgentEvent

        yield AgentEvent(
            type="done",
            data={},
        )
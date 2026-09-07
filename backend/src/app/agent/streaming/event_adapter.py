from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from app.agent.events import AgentEvent


class SSEEventAdapter:

    async def adapt(
        self,
        events: AsyncIterator[dict[str, Any]],
    ) -> AsyncIterator[AgentEvent]:

        async for event in events:

            event_type = event.get(
                "event"
            )

            data = event.get(
                "data",
                {},
            )

            # -------------------------
            # LLM Streaming
            # -------------------------

            if event_type == "on_chat_model_stream":

                chunk = data.get(
                    "chunk"
                )

                if chunk is None:
                    continue

                content = getattr(
                    chunk,
                    "content",
                    "",
                )

                if content:

                    yield AgentEvent(
                        type="message_delta",
                        data={
                            "content": content,
                        },
                    )

                continue

            # -------------------------
            # Tool Start
            # -------------------------

            if event_type == "on_tool_start":

                name = event.get(
                    "name",
                    "unknown",
                )

                input_data = data.get(
                    "input",
                    {},
                )

                yield AgentEvent(
                    type="tool_start",
                    data={
                        "tool": name,
                        "arguments": input_data,
                    },
                )

                continue

            # -------------------------
            # Tool End
            # -------------------------

            if event_type == "on_tool_end":

                name = event.get(
                    "name",
                    "unknown",
                )

                output = data.get(
                    "output"
                )

                yield AgentEvent(
                    type="tool_end",
                    data={
                        "tool": name,
                        "result": output,
                    },
                )

                continue
from __future__ import annotations

from langgraph.prebuilt import ToolNode


class MCPToolNode:

    def __init__(self, tools: list):

        self.tools = tools

        self.node = ToolNode(
            tools,
        )

    async def __call__(self, state):

        return await self.node.ainvoke(
            state
        )
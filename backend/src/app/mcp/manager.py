from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool

from .client import THSMCPClient


class MCPManager:

    def __init__(self):
        self.client = THSMCPClient()
        self._tools: list[BaseTool] | None = None

    async def initialize(self) -> None:
        if self._tools is not None:
            return

        self._tools = await self.client.get_tools()

    async def get_tools(self) -> list[BaseTool]:
        await self.initialize()
        return self._tools or []

    async def get_tool(self, name: str) -> BaseTool | None:
        tools = await self.get_tools()

        for tool in tools:
            if tool.name == name:
                return tool

        return None

    async def list_tools(self) -> list[dict[str, Any]]:
        tools = await self.get_tools()

        return [
            {
                "name": tool.name,
                "description": tool.description,
            }
            for tool in tools
        ]
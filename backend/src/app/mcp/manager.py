from __future__ import annotations

import logging
from typing import Any, Iterable

from .registry import (
    MCPToolDefinition,
    MCPToolRegistry,
    ToolCapability,
    ToolDomain,
    ToolIntent,
)
from .service import MCPService

logger = logging.getLogger(__name__)


class MCPManager:
    """
    MCP 生命周期与 Tool 装配管理器。

    职责：

    1. 管理 MCP Tools
    2. 创建 MCPService
    3. 根据 Agent 场景筛选 Tools
    4. 向 LangGraph 提供 Tools
    5. 提供 Tool 信息查询

    不负责：
    - LLM 调用
    - Agent 推理
    - RAG
    - SSE
    """

    def __init__(
        self,
        *,
        tools: list[Any],
        registry: MCPToolRegistry,
    ):
        self.tools = tools
        self.registry = registry

        self.service = MCPService(
            tools=tools,
            registry=registry,
        )

        self._tool_map = {
            tool.name: tool
            for tool in tools
            if getattr(tool, "name", None)
        }

    # =========================================================
    # Tool
    # =========================================================

    def get_tool(
        self,
        name: str,
    ) -> Any:

        return self.service.get_tool(name)

    def get_all_tools(self) -> list[Any]:
        return list(self._tool_map.values())

    # =========================================================
    # Agent Tools
    # =========================================================

    def get_agent_tools(
        self,
        *,
        intents: Iterable[ToolIntent] | None = None,
        domains: Iterable[ToolDomain] | None = None,
        capabilities: Iterable[ToolCapability] | None = None,
    ) -> list[Any]:
        """
        为 Agent 装配 Tools。

        可以按照：

        Intent
        Domain
        Capability

        三种方式筛选。
        """

        definitions = self.registry.get(
            intents=intents,
            domains=domains,
            capabilities=capabilities,
        )

        tools: list[Any] = []

        for definition in definitions:

            tool = self._tool_map.get(
                definition.name
            )

            if tool is not None:
                tools.append(tool)

        logger.info(
            "Loaded agent tools: %s",
            [tool.name for tool in tools],
        )

        return tools

    # =========================================================
    # 常用 Agent Tool 集
    # =========================================================

    def get_market_tools(self) -> list[Any]:
        """
        市场分析 Agent。

        首页宏观数据、市场概览、指数分析等场景。
        """

        return self.get_agent_tools(
            intents={
                ToolIntent.MARKET_OVERVIEW,
                ToolIntent.INDEX_ANALYSIS,
            }
        )

    def get_stock_tools(self) -> list[Any]:
        """
        股票分析 Agent。
        """

        return self.get_agent_tools(
            intents={
                ToolIntent.STOCK_ANALYSIS,
                ToolIntent.STOCK_FINANCIAL,
            }
        )

    def get_fund_tools(self) -> list[Any]:

        return self.get_agent_tools(
            domains={
                ToolDomain.FUND,
            }
        )

    def get_macro_tools(self) -> list[Any]:

        return self.get_agent_tools(
            domains={
                ToolDomain.MACRO,
            }
        )

    def get_news_tools(self) -> list[Any]:

        return self.get_agent_tools(
            capabilities={
                ToolCapability.NEWS,
            }
        )

    # =========================================================
    # Tool 信息
    # =========================================================

    def describe(
        self,
        tool_name: str,
    ) -> dict[str, Any]:

        return self.service.describe_tool(
            tool_name
        )

    def list_tools(self) -> list[dict[str, Any]]:

        return self.service.describe_tools()
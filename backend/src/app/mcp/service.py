from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Iterable

from .registry import (
    MCPToolDefinition,
    MCPToolRegistry,
    ToolCapability,
    ToolDomain,
    ToolIntent,
)

logger = logging.getLogger(__name__)


class MCPServiceError(Exception):
    """MCP Service 基础异常。"""


class MCPToolNotFoundError(MCPServiceError):
    """MCP Tool 不存在。"""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        super().__init__(f"MCP tool not found: {tool_name}")


class MCPToolExecutionError(MCPServiceError):
    """MCP Tool 执行失败。"""

    def __init__(
        self,
        tool_name: str,
        message: str,
        *,
        cause: Exception | None = None,
    ):
        self.tool_name = tool_name
        self.cause = cause
        super().__init__(
            f"MCP tool execution failed: "
            f"{tool_name}: {message}"
        )


@dataclass(slots=True)
class MCPToolCallResult:
    """
    MCP Tool 调用结果。

    这个对象不仅供业务层使用，
    后面 SSE 流式输出 Tool Call 时也可以直接使用。
    """

    tool_name: str

    success: bool

    data: Any = None

    error: str | None = None

    elapsed_ms: float = 0.0

    # Tool 的业务元数据
    definition: MCPToolDefinition | None = None

    # 实际传递给 MCP Tool 的参数
    arguments: dict[str, Any] | None = None


class MCPService:
    """
    MCP 业务服务层。

    职责：

    1. 管理 MCP Tool
    2. 根据名称调用 Tool
    3. 根据 Intent 筛选 Tool
    4. 根据 Domain / Capability 筛选 Tool
    5. 统一异常处理
    6. 统一返回结构
    7. 为 Agent / Dashboard / SSE 提供统一入口

    注意：

    MCPService 不负责：
    - MCP Server 连接
    - DeepSeek 调用
    - LangGraph Agent
    - RAG
    """

    def __init__(
        self,
        *,
        tools: Iterable[Any],
        registry: MCPToolRegistry | None = None,
    ):
        self.registry = registry or MCPToolRegistry()

        # MCP Server 实际返回的 Tool 实例
        self._tools: dict[str, Any] = {
            tool.name: tool
            for tool in tools
            if getattr(tool, "name", None)
        }

    # =========================================================
    # Tool 查询
    # =========================================================

    def list_tools(self) -> list[Any]:
        """
        获取当前 MCP Server 提供的所有 Tool。
        """

        return list(self._tools.values())

    def get_tool(
        self,
        tool_name: str,
    ) -> Any:
        """
        根据 Tool Name 获取真实 MCP Tool。
        """

        tool = self._tools.get(tool_name)

        if tool is None:
            raise MCPToolNotFoundError(tool_name)

        return tool

    def get_definition(
        self,
        tool_name: str,
    ) -> MCPToolDefinition | None:
        """
        获取 Tool 的 Registry 元数据。
        """

        return self.registry.get_definition(tool_name)

    # =========================================================
    # Tool 筛选
    # =========================================================

    def get_tools_by_intent(
        self,
        intent: ToolIntent,
    ) -> list[Any]:
        """
        根据 Agent Intent 获取真实 MCP Tools。

        示例：

            STOCK_FINANCIAL
                ↓
            get_stock_financials
        """

        definitions = self.registry.get_by_intent(intent)

        return self._resolve_definitions(definitions)

    def get_tools_by_domain(
        self,
        domain: ToolDomain,
    ) -> list[Any]:

        definitions = self.registry.get_by_domain(domain)

        return self._resolve_definitions(definitions)

    def get_tools_by_capability(
        self,
        capability: ToolCapability,
    ) -> list[Any]:

        definitions = self.registry.get_by_capability(
            capability
        )

        return self._resolve_definitions(definitions)

    def get_tools(
        self,
        *,
        domains: Iterable[ToolDomain] | None = None,
        capabilities: Iterable[ToolCapability] | None = None,
        intents: Iterable[ToolIntent] | None = None,
    ) -> list[Any]:
        """
        多条件获取 MCP Tools。
        """

        definitions = self.registry.get(
            domains=domains,
            capabilities=capabilities,
            intents=intents,
        )

        return self._resolve_definitions(definitions)

    def _resolve_definitions(
        self,
        definitions: Iterable[MCPToolDefinition],
    ) -> list[Any]:

        tools = []

        for definition in definitions:
            tool = self._tools.get(definition.name)

            if tool is not None:
                tools.append(tool)

        return tools

    # =========================================================
    # Tool 调用
    # =========================================================

    async def call(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> MCPToolCallResult:
        """
        调用 MCP Tool。

        兼容 LangChain Runnable Tool：

            await tool.ainvoke(arguments)

        也可以兼容普通 async callable。
        """

        arguments = arguments or {}

        tool = self.get_tool(tool_name)

        definition = self.registry.get_definition(
            tool_name
        )

        start = time.perf_counter()

        try:
            logger.info(
                "MCP tool call: name=%s arguments=%s",
                tool_name,
                arguments,
            )

            result = await self._invoke_tool(
                tool,
                arguments,
            )

            elapsed_ms = (
                time.perf_counter() - start
            ) * 1000

            logger.info(
                "MCP tool success: name=%s elapsed_ms=%.2f",
                tool_name,
                elapsed_ms,
            )

            return MCPToolCallResult(
                tool_name=tool_name,
                success=True,
                data=result,
                elapsed_ms=elapsed_ms,
                definition=definition,
                arguments=arguments,
            )

        except Exception as exc:
            elapsed_ms = (
                time.perf_counter() - start
            ) * 1000

            logger.exception(
                "MCP tool failed: name=%s type=%s",
                tool_name,
                type(exc).__name__,
            )

            error_message = self._format_exception(exc)

            return MCPToolCallResult(
                tool_name=tool_name,
                success=False,
                error=error_message,
                elapsed_ms=elapsed_ms,
                definition=definition,
                arguments=arguments,
            )

    async def _invoke_tool(
        self,
        tool: Any,
        arguments: dict[str, Any],
    ) -> Any:

        # -----------------------------------------------------
        # LangChain BaseTool / StructuredTool
        # -----------------------------------------------------
        if hasattr(tool, "ainvoke"):
            return await tool.ainvoke(arguments)

        # -----------------------------------------------------
        # 普通 async callable
        # -----------------------------------------------------

        if callable(tool):
            result = tool(**arguments)

            if isinstance(result, Awaitable):
                return await result

            return result

        raise TypeError(
            f"Unsupported MCP tool type: "
            f"{type(tool).__name__}"
        )

    # =========================================================
    # 强制调用
    # =========================================================

    async def call_or_raise(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        """
        调用 Tool。

        如果失败直接抛异常。

        适合：
        - Dashboard API
        - 内部业务服务

        不适合：
        - SSE
        - Agent 流式调用
        """

        result = await self.call(
            tool_name,
            arguments,
        )

        if not result.success:
            raise MCPToolExecutionError(
                tool_name,
                result.error or "unknown error",
            )

        return result.data

    # =========================================================
    # Agent 专用
    # =========================================================

    def get_agent_tools(
        self,
        intent: ToolIntent,
    ) -> list[Any]:
        """
        获取某个 Agent 场景需要的 Tools。

        例如：

            ToolIntent.STOCK_FINANCIAL

        返回：

            get_stock_financials
        """

        return self.get_tools_by_intent(intent)

    # =========================================================
    # Dashboard 专用
    # =========================================================

    async def call_dashboard_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        """
        首页 Dashboard 专用调用入口。

        Dashboard 不需要关心 MCPToolCallResult，
        直接获得 MCP 返回的数据。
        """

        return await self.call_or_raise(
            tool_name,
            arguments,
        )

    # =========================================================
    # Tool 信息
    # =========================================================

    def describe_tool(
        self,
        tool_name: str,
    ) -> dict[str, Any]:

        tool = self.get_tool(tool_name)

        definition = self.registry.get_definition(
            tool_name
        )

        return {
            "name": tool_name,
            "description": getattr(
                tool,
                "description",
                definition.description
                if definition
                else "",
            ),
            "domain": (
                definition.domain.value
                if definition
                else None
            ),
            "capability": (
                definition.capability.value
                if definition
                else None
            ),
            "intents": (
                [x.value for x in definition.intents]
                if definition
                else []
            ),
        }

    def describe_tools(
        self,
        tools: Iterable[Any] | None = None,
    ) -> list[dict[str, Any]]:

        if tools is None:
            tools = self.list_tools()

        return [
            self.describe_tool(tool.name)
            for tool in tools
        ]

    # =========================================================
    # 异常处理
    # =========================================================

    def _format_exception(
        self,
        exc: BaseException,
    ) -> str:
        """
        展开 ExceptionGroup / TaskGroup，
        避免只看到：
            unhandled errors in a TaskGroup
        """

        if isinstance(exc, BaseExceptionGroup):
            errors: list[str] = []

            for sub_exc in exc.exceptions:
                errors.append(
                    self._format_exception(sub_exc)
                )

            return " | ".join(errors)

        return (
            f"{type(exc).__name__}: {exc}"
        )
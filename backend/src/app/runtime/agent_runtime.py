# app/runtime/agent_runtime.py

from typing import Dict
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)
from app.rag.factory import create_rag_service
from langgraph.graph.state import CompiledStateGraph

from app.agent.factory import AgentFactory
from app.mcp.client import THSMCPClient
from app.mcp.manager import MCPManager
from app.mcp.registry import MCPToolRegistry
from app.rag.service import RagService
from app.llm.deepseek import create_deepseek


class AgentRuntime:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.mcp_client: THSMCPClient | None = None
        self.mcp_manager: MCPManager | None = None
        self.rag_service: RagService | None = None
        self.session_factory: async_sessionmaker[AsyncSession] = session_factory

        self.agent_factory: AgentFactory | None = None
        self.graphs: Dict[str, CompiledStateGraph] = {}

    async def startup(self):
        """
        应用启动时执行
        """

        # 1. MCP
        print("初始化 MCP...")

        if not self.mcp_client:
            self.mcp_client = THSMCPClient()

        registry = MCPToolRegistry()

        tools = await self.mcp_client.get_tools()

        if not self.mcp_manager:
            self.mcp_manager = MCPManager(
                tools=tools,
                registry=registry,
            )

        # 2. LLM
        print("初始化 LLM...")

        llm = create_deepseek()

        market_tools = self.mcp_manager.get_market_tools()

        market_llm = llm.bind_tools(
            tools=market_tools
        )

        # 3. RAG
        if not self.rag_service:
            print("初始化 RAG...")
            self.rag_service = create_rag_service(self.session_factory)

        # 4. AgentFactory
        print("初始化 AgentFactory...")

        self.agent_factory = AgentFactory(
            llm=market_llm,
            mcp_manager=self.mcp_manager,
            rag_service=self.rag_service,
        )

        # 5. 创建 Graph
        print("创建 Market Agent...")

        self.graphs["market"] = self.agent_factory.create(
            agent_type="market"
        )

        print("Agent Runtime 初始化完成")

    def get_graph(self, agent_type: str):
        graph = self.graphs.get(agent_type)

        if graph is None:
            raise ValueError(
                f"Agent not found: {agent_type}"
            )

        return graph

    async def shutdown(self):
        """
        应用关闭时执行
        """

        print("关闭 Agent Runtime...")
        self.graphs.clear()

        self.agent_factory = None
        self.mcp_manager = None
        self.mcp_client = None
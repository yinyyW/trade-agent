from __future__ import annotations

from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from app.agent.nodes.llm import LLMNode
from app.agent.nodes.rag import RAGNode
from app.agent.router import route_after_llm
from app.agent.state import AgentState
from app.mcp.manager import MCPManager
from app.rag.service import RAGService


class AgentFactory:

    def __init__(
        self,
        *,
        llm: ChatOpenAI,
        rag_service: RAGService,
        mcp_manager: MCPManager,
    ):
        self.llm = llm
        self.rag_service = rag_service
        self.mcp_manager = mcp_manager

    def create(
        self,
        *,
        agent_type: str = "general",
    ):

        tools = self._get_tools(
            agent_type
        )

        # DeepSeek 必须绑定 Tool
        llm_with_tools = self.llm.bind_tools(
            tools
        )

        rag_node = RAGNode(
            self.rag_service,
            top_k=5,
        )

        llm_node = LLMNode(
            llm_with_tools
        )

        tool_node = ToolNode(
            tools
        )

        graph = StateGraph(
            AgentState
        )

        # ---------------------------
        # Nodes
        # ---------------------------

        graph.add_node(
            "rag",
            rag_node,
        )

        graph.add_node(
            "llm",
            llm_node,
        )

        graph.add_node(
            "mcp",
            tool_node,
        )

        # ---------------------------
        # Edges
        # ---------------------------

        graph.add_edge(
            START,
            "rag",
        )

        graph.add_edge(
            "rag",
            "llm",
        )

        graph.add_conditional_edges(
            "llm",
            route_after_llm,
            {
                "mcp": "mcp",
                "end": END,
            },
        )

        # Tool 执行完成后重新进入 LLM
        graph.add_edge(
            "mcp",
            "llm",
        )

        return graph.compile()

    def _get_tools(
        self,
        agent_type: str,
    ) -> list:

        if agent_type == "market":
            return self.mcp_manager.get_market_tools()

        if agent_type == "stock":
            return self.mcp_manager.get_stock_tools()

        if agent_type == "macro":
            return self.mcp_manager.get_macro_tools()

        if agent_type == "fund":
            return self.mcp_manager.get_fund_tools()

        if agent_type == "news":
            return self.mcp_manager.get_news_tools()

        # MVP
        #
        # General Agent 不建议直接暴露所有 MCP Tool。
        #
        # 如果当前阶段需要全部工具，可以：
        return self.mcp_manager.get_all_tools()
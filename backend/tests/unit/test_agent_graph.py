import asyncio

from app.agent.factory import AgentFactory
from app.agent.nodes.llm import LLMNode
from app.agent.nodes.rag import RAGNode
from app.llm.deepseek import create_deepseek
from app.rag.factory import create_rag_service
from app.rag.service import RagService
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from app.mcp.client import THSMCPClient
from app.mcp.manager import MCPManager
from app.mcp.registry import MCPToolRegistry
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.rag.config import database_settings

def create_session_factory():
    database_url = getattr(database_settings, "database_url", None)

    if not database_url:
        raise RuntimeError(
            "未配置 database_url，请在 .env 中配置 DATABASE_URL"
        )

    engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
    )

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return engine, session_factory

SYSTEM_PROMPT = """
你是一个专业的金融 AI Agent。

你的主要职责：

1. 回答金融、证券、宏观经济、基金、债券、期货等问题。
2. 对实时、历史、财务、行情类数据，优先使用 MCP 工具获取真实数据。
3. 对金融概念、理论、分析方法，优先参考 RAG 知识库。
4. 如果问题同时需要知识和实时数据，可以同时使用 RAG 和 MCP。
5. 不要编造金融数据。
6. 如果工具没有返回相关数据，明确告诉用户。
7. 对数据进行分析时，需要区分：
   - 客观数据
   - 数据推导
   - 主观判断
8. 不构成投资建议。

回答尽量清晰、专业，并说明关键数据来源。
"""

async def test_llm():
    # 创建 RAG 服务
    print("创建RAG服务...")
    engine, session_factory = create_session_factory()
    rag_service = None
    try:
        async with session_factory() as session:
            rag_service = create_rag_service(session=session)
            # 创建模型和工具
            client = THSMCPClient()
            registry = MCPToolRegistry()
            print("获取工具...")
            tools = await client.get_tools()
            manager = MCPManager(tools=tools, registry=registry)
            market_tools = manager.get_market_tools()
        
            llm = create_deepseek()
            llm = llm.bind_tools(
                tools=market_tools
            )
        
            # 创建 agent
            if not rag_service:
                print("未获取到RAG服务")
                return
            factory = AgentFactory(llm=llm, mcp_manager=manager, rag_service=rag_service)
            print("创建agent成功")
            graph = factory.create(agent_type="market")
        
            # 测试请求
            print("测试智能体请求")
            result = await graph.ainvoke(
                {
                    "messages": [HumanMessage(content="现在沪深300指数基金怎么样？")],
                }
            )
            messages = result["messages"]

            last_message = messages[-1]

            if isinstance(last_message, AIMessage):
                print("AI 回复：")
                print(last_message.content)
    finally:
            await engine.dispose()



if __name__ == "__main__":
    asyncio.run(test_llm())
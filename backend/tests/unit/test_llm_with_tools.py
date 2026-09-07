import asyncio

from app.agent.nodes.llm import LLMNode
from app.agent.nodes.rag import RAGNode
from app.llm.deepseek import create_deepseek
from app.rag.factory import create_rag_service
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from app.mcp.client import THSMCPClient
from app.mcp.manager import MCPManager
from app.mcp.registry import MCPToolRegistry

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

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content="分析下当前A股市场"),
    ]

    # loop agent 执行命令
    while (True):
        print("异步发送请求...")
        response = await llm.ainvoke(messages)
        print(f"AI 回复消息: {response}")

        # 添加AI回复
        messages.append(response)

        # 解析AI回复
        if (not response.tool_calls):
            print("\n========== 最终答案 ==========")
            print(response.content)
            break

        # 执行工具调用
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]
            print(f"执行工具 [{tool_name}]")                                                
            print(f"工具参数: {tool_args}")

            tool = next(tool for tool in tools if tool.name == tool_name)
            if (not tool):
                print(f"未找到工具: {tool_name}")
                continue
            tool_response = await tool.ainvoke(tool_args)
            print(f"工具调用结果: {tool_response}")

            # 添加工具调用结果至消息
            messages.append(ToolMessage(
                content=str(tool_response),
                tool_call_id=tool_id
            ))


if __name__ == "__main__":
    asyncio.run(test_llm())
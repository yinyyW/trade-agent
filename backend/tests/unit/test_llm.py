import asyncio

from app.agent.nodes.llm import LLMNode
from app.agent.nodes.rag import RAGNode
from app.llm.deepseek import create_deepseek
from app.rag.factory import create_rag_service
from langchain_core.messages import HumanMessage, SystemMessage

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
    llm = create_deepseek()

    messages = [
        HumanMessage(content="请解释下10年期美债收益率增加对资本市场的影响")
    ]

    input_messages = [
        SystemMessage(
            content=SYSTEM_PROMPT
        ),
        *messages,
    ]

    print("Sending request asynchronously...")
    response = await llm.ainvoke(
        input=input_messages
    )

    # 4. Print the text content of the response
    print("\nResult:")
    print(response.content)


if __name__ == "__main__":
    asyncio.run(test_llm())
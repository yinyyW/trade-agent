from __future__ import annotations

from langchain.agents import create_agent

from app.llm.deepseek import create_deepseek
from app.mcp.manager import MCPManager


class TradeAgent:

    def __init__(
        self,
        llm,
        tools,
    ):
        self.llm = llm
        self.tools = tools

        self.agent = create_agent(
            model=self.llm,
            tools=self.tools
        )

    async def ainvoke(
        self,
        message: str,
    ):
        return await self.agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": message,
                    }
                ]
            }
        )


async def create_trade_agent() -> TradeAgent:

    llm = create_deepseek()

    manager = MCPManager()

    tools = await manager.get_tools()

    return TradeAgent(
        llm=llm,
        tools=tools,
    )
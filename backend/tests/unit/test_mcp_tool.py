import asyncio

from app.mcp.client import THSMCPClient
from app.mcp.manager import MCPManager
from app.mcp.registry import MCPToolRegistry


async def test_query_tools():
    client = THSMCPClient()
    tools = await client.get_tools()

    print("\n=== MCP Tools ===")

    for tool in tools:
        print(f"\nName: {tool.name}")
        print(f"Description: {tool.description}")



async def test_invoke_tool():

    client = THSMCPClient()
    registry = MCPToolRegistry()
    tools = await client.get_tools()
    manager = MCPManager(tools=tools, registry=registry)

    tool = manager.get_tool(
        "index_highfreq_quotes"
    )
    if tool is None:
        raise RuntimeError("MCP tool not found")

    result = await tool.ainvoke(
        {
            "symbols": "000001.SH,000941,创业板指",
            "indicators": "最高价,最新价,涨跌幅,动态市盈率,上涨家数",
            "data_mode": "real_time"
        }
    )

    print(f"ai工具调用结果：{result}")

if __name__ == "__main__":
    asyncio.run(test_invoke_tool())
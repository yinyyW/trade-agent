import asyncio

from app.mcp.manager import MCPManager


async def test_query_tools():

    manager = MCPManager()

    tools = await manager.get_tools()

    print("\n=== MCP Tools ===")

    for tool in tools:
        print(f"\nName: {tool.name}")
        print(f"Description: {tool.description}")

async def test_invoke_tool():

    manager = MCPManager()

    tool = await manager.get_tool(
        "index_highfreq_quotes"
    )
    print(tool.args_schema)

    if tool is None:
        raise RuntimeError("MCP tool not found")

    result = await tool.ainvoke(
        {
            "symbols": "000001.SH,000941,创业板指",
            "indicators": "最高价,最新价,涨跌幅,动态市盈率,上涨家数",
            "data_mode": "real_time"
        }
    )

    print(result)

if __name__ == "__main__":
    asyncio.run(test_invoke_tool())
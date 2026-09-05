import asyncio

from app.mcp.client import THSMCPClient
from app.mcp.manager import MCPManager
from app.mcp.registry import MCPToolRegistry


async def test_market_manager():
    client = THSMCPClient()
    registry = MCPToolRegistry()
    tools = await client.get_tools()
    manager = MCPManager(tools=tools, registry=registry)
    macro_tools = manager.get_market_tools()
    for tool in macro_tools:
        print(f"市场工具：{tool.name}")

async def test_macro_manager():
    client = THSMCPClient()
    registry = MCPToolRegistry()
    tools = await client.get_tools()
    manager = MCPManager(tools=tools, registry=registry)
    macro_tools = manager.get_macro_tools()
    for tool in macro_tools:
        print(f"宏观工具：{tool.name}")


if __name__ == "__main__":
    asyncio.run(test_macro_manager())
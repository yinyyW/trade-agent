import asyncio

from app.mcp.manager import MCPManager


async def main():

    manager = MCPManager()

    tools = await manager.get_tools()

    print("\n=== MCP Tools ===")

    for tool in tools:
        print(f"\nName: {tool.name}")
        print(f"Description: {tool.description}")


if __name__ == "__main__":
    asyncio.run(main())
import asyncio

from app.mcp.client import THSMCPClient
from app.mcp.service import MCPService


async def test_dashboard_mcp(mcp_service: MCPService):
  	await mcp_service.call_dashboard_tool(
        "index_highfreq_quotes",
        {
            "symbols": "000001.SH,000941,创业板指",
            "indicators": "最高价,最新价,涨跌幅,动态市盈率,上涨家数",
            "data_mode": "real_time",
        },
    )

async def main():
	client = THSMCPClient()
	tools = await client.get_tools()
	service = MCPService(tools=tools)
	result = await test_dashboard_mcp(service)
	print(f"result = {result}")

if __name__ == "__main__":
    asyncio.run(main())
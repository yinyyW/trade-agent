from __future__ import annotations

from langchain_mcp_adapters.client import MultiServerMCPClient

from .config import mcp_settings

class THSMCPClient:

    def __init__(self):
        self.client = MultiServerMCPClient(
            {
                "hexin-ifind-ds-stock-mcp": {
                    "headers": {
                        "Authorization": mcp_settings.ths_mcp_api_key
                    },
                    "transport": mcp_settings.ths_mcp_transport,
                    "url": f"{mcp_settings.ths_mcp_base_url}/hexin-ifind-ds-stock-mcp",
                },
                "hexin-ifind-ds-fund-mcp": {
                    "headers": {
                        "Authorization": mcp_settings.ths_mcp_api_key
                    },
                    "transport": mcp_settings.ths_mcp_transport,
                    "url": f"{mcp_settings.ths_mcp_base_url}/hexin-ifind-ds-fund-mcp",
                },
                "hexin-ifind-ds-edb-mcp": {
                    "headers": {
                        "Authorization": mcp_settings.ths_mcp_api_key
                    },
                    "transport": mcp_settings.ths_mcp_transport,
                    "url": f"{mcp_settings.ths_mcp_base_url}/hexin-ifind-ds-edb-mcp",
                },
                "hexin-ifind-ds-news-mcp": {
                    "headers": {
                        "Authorization": mcp_settings.ths_mcp_api_key
                    },
                    "transport": mcp_settings.ths_mcp_transport,
                    "url": f"{mcp_settings.ths_mcp_base_url}/hexin-ifind-ds-news-mcp",
                },
                "hexin-ifind-ds-bond-mcp": {
                    "headers": {
                        "Authorization": mcp_settings.ths_mcp_api_key
                    },
                    "transport": mcp_settings.ths_mcp_transport,
                    "url": f"{mcp_settings.ths_mcp_base_url}/hexin-ifind-ds-bond-mcp",
                },
                "hexin-ifind-ds-global-stock-mcp": {
                    "headers": {
                        "Authorization": mcp_settings.ths_mcp_api_key
                    },
                    "transport": mcp_settings.ths_mcp_transport,
                    "url": f"{mcp_settings.ths_mcp_base_url}/hexin-ifind-ds-global-stock-mcp",
                },
                "hexin-ifind-ds-index-mcp": {
                    "headers": {
                        "Authorization": mcp_settings.ths_mcp_api_key
                    },
                    "transport": mcp_settings.ths_mcp_transport,
                    "url": f"{mcp_settings.ths_mcp_base_url}/hexin-ifind-ds-index-mcp",
                },
                "hexin-ifind-ds-futures-mcp": {
                    "headers": {
                        "Authorization": mcp_settings.ths_mcp_api_key
                    },
                    "transport": mcp_settings.ths_mcp_transport,
                    "url": f"{mcp_settings.ths_mcp_base_url}/hexin-ifind-ds-futures-mcp",
                }
            }
        )

    async def get_tools(self):
        return await self.client.get_tools()
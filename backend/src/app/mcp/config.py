from pydantic_settings import BaseSettings, SettingsConfigDict


class MCPSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ths_mcp_api_key: str = ""
    ths_mcp_base_url: str = "https://fuyao.aicubes.cn"
    ths_mcp_transport: str = "streamable_http"


mcp_settings = MCPSettings()
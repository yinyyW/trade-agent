# dependencies.py

from functools import lru_cache

from app.home.service import HomeService
from app.market.repository.akshare_market import AkshareMarketRepository
from app.market.service import IndicatorService, MarketService
from fastapi import Request

from app.runtime.runtime import ApplicationRuntime
from app.home.providers.akshare_providers import AkShareMarketProvider, AkShareSectorProvider, AkShareNewsProvider


def get_runtime(request: Request) -> ApplicationRuntime:
    return request.app.state.runtime

@lru_cache
def get_home_service(request: Request) -> HomeService:
    runtime = get_runtime(request=request)
    agent = runtime.agent_runtime
    return HomeService(
        market_provider=AkShareMarketProvider(),
        sector_provider=AkShareSectorProvider(),
        news_provider=AkShareNewsProvider(),
        mcp_manager=agent.mcp_manager
    )

@lru_cache
def get_market_service() -> MarketService:

    repository = AkshareMarketRepository()

    indicator_service = IndicatorService()

    return MarketService(
        repository=repository,
        indicator_service=indicator_service,
    )
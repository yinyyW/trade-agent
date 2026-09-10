from __future__ import annotations

from .domain.candle import Candle
from .indicators import INDICATOR_REGISTRY
from .indicators.base import IndicatorResult
from .domain.timeframe import AdjustType, KlinePeriod
from .repository.akshare_market import MarketRepository

class IndicatorService:

    def calculate(
        self,
        candles: list[Candle],
        indicators: list[dict],
    ) -> list[IndicatorResult]:
        results = []

        for request in indicators:

            name = request["name"].upper()

            indicator = INDICATOR_REGISTRY.get(name)

            if indicator is None:
                raise ValueError(
                    f"Unsupported indicator: {name}"
                )

            params = request.get(
                "params",
                {},
            )

            result = indicator.calculate(
                candles,
                params,
            )

            results.append(result)

        return results

class MarketService:

    def __init__(
        self,
        repository: MarketRepository,
        indicator_service: IndicatorService,
    ):
        self.repository = repository
        self.indicator_service = indicator_service

    async def get_kline(
        self,
        symbol: str,
        period: KlinePeriod,
        adjust: AdjustType,
        start,
        end,
        indicators,
    ):
        candles = await self.repository.get_kline(
            symbol=symbol,
            period=period,
            adjust=adjust,
            start=start,
            end=end,
        )

        indicator_results = (
            self.indicator_service.calculate(
                candles=candles,
                indicators=[
                    item.model_dump()
                    for item in indicators
                ],
            )
        )

        return candles, indicator_results
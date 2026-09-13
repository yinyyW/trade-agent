from __future__ import annotations
from functools import lru_cache
import akshare as ak

from .domain.candle import Candle
from .indicators import INDICATOR_REGISTRY
from .indicators.base import IndicatorResult
from .domain.timeframe import AdjustType, KlinePeriod
from .repository.akshare_market import MarketRepository


@lru_cache(maxsize=1)
def get_stock_map() -> dict[str, str]:
    df = ak.stock_info_a_code_name()

    return dict(
        zip(
            df["code"].astype(str),
            df["name"].astype(str),
        )
    )

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

    def get_stock_name(self, symbol: str) -> str | None:
        stock_map = get_stock_map()
        code = self._convert_symbot_to_code(symbol=symbol)
        return stock_map.get(code)

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

    def _convert_symbot_to_code(self, symbol):
        symbol = symbol.upper().strip()

        if "." in symbol:
            parts = symbol.split(".")
            return parts[-1]

        if len(symbol) > 6:
            return symbol[-6:]

        return symbol
from __future__ import annotations

from decimal import Decimal
from typing import Any

from .base import (
    Indicator,
    IndicatorResult,
    IndicatorSeriesResult,
)
from ..domain.candle import Candle


class MAIndicator(Indicator):

    name = "MA"
    type = "overlay"

    def calculate(
        self,
        candles: list[Candle],
        params: dict[str, Any],
    ) -> IndicatorResult:
        periods = [
            self.validate_period(int(p))
            for p in params.get(
                "periods",
                [5, 10, 20],
            )
        ]
        periods = sorted(set(int(p) for p in periods))

        close_prices = [
            candle.close
            for candle in candles
        ]

        series = []

        for period in periods:
            values = self._calculate_ma(
                close_prices,
                period,
            )

            series.append(
                IndicatorSeriesResult(
                    name=f"MA{period}",
                    values=values,
                )
            )

        return IndicatorResult(
            name=self.name,
            type=self.type,
            params={
                "periods": periods,
            },
            series=series,
        )

    @staticmethod
    def _calculate_ma(
        prices: list[Decimal],
        period: int,
    ) -> list[Decimal | None]:

        result: list[Decimal | None] = []

        window_sum = Decimal("0")

        for i, price in enumerate(prices):

            window_sum += price

            if i >= period:
                window_sum -= prices[i - period]

            if i < period - 1:
                result.append(None)
            else:
                result.append(
                    window_sum / Decimal(period)
                )

        return result
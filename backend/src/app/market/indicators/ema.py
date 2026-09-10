from __future__ import annotations

from decimal import Decimal
from typing import Any

from .base import (
    Indicator,
    IndicatorResult,
    IndicatorSeriesResult,
)
from ..domain.candle import Candle


class EMAIndicator(Indicator):

    name = "EMA"
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

        periods = sorted(
            set(int(p) for p in periods)
        )

        prices = [
            candle.close
            for candle in candles
        ]

        series = []

        for period in periods:

            values = self._calculate_ema(
                prices,
                period,
            )

            series.append(
                IndicatorSeriesResult(
                    name=f"EMA{period}",
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
    def _calculate_ema(
        prices: list[Decimal],
        period: int,
    ) -> list[Decimal | None]:

        result: list[Decimal | None] = []

        if len(prices) < period:
            return [None] * len(prices)

        alpha = Decimal("2") / Decimal(period + 1)

        # 第一个 EMA 使用 SMA 初始化
        initial_sum = sum(
            prices[:period],
            Decimal("0"),
        )

        ema = initial_sum / Decimal(period)

        for i, price in enumerate(prices):

            if i < period - 1:
                result.append(None)

            elif i == period - 1:
                result.append(ema)

            else:
                ema = (
                    price * alpha
                    + ema * (Decimal("1") - alpha)
                )

                result.append(ema)

        return result
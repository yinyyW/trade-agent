from __future__ import annotations

from decimal import Decimal
from math import sqrt
from typing import Any

from .base import (
    Indicator,
    IndicatorResult,
    IndicatorSeriesResult,
)
from ..domain.candle import Candle


class BOLLIndicator(Indicator):

    name = "BOLL"
    type = "overlay"

    def calculate(
        self,
        candles: list[Candle],
        params: dict[str, Any],
    ) -> IndicatorResult:
        period = self.validate_period(int(params.get("period", 20)))

        std_multiplier = Decimal(
            str(params.get("std", 2))
        )

        prices = [
            candle.close
            for candle in candles
        ]

        middle: list[Decimal | None] = []
        upper: list[Decimal | None] = []
        lower: list[Decimal | None] = []

        for i in range(len(prices)):

            if i < period - 1:
                middle.append(None)
                upper.append(None)
                lower.append(None)
                continue

            window = prices[
                i - period + 1:
                i + 1
            ]

            mean = (
                sum(window, Decimal("0"))
                / Decimal(period)
            )

            variance = (
                sum(
                    (price - mean) ** 2
                    for price in window
                )
                / Decimal(period)
            )

            std = Decimal(
                str(sqrt(float(variance)))
            )

            middle_value = mean

            upper_value = (
                mean
                + std_multiplier * std
            )

            lower_value = (
                mean
                - std_multiplier * std
            )

            middle.append(middle_value)
            upper.append(upper_value)
            lower.append(lower_value)

        return IndicatorResult(
            name=self.name,
            type=self.type,
            params={
                "period": period,
                "std": std_multiplier,
            },
            series=[
                IndicatorSeriesResult(
                    name="upper",
                    values=upper,
                ),
                IndicatorSeriesResult(
                    name="middle",
                    values=middle,
                ),
                IndicatorSeriesResult(
                    name="lower",
                    values=lower,
                ),
            ],
        )
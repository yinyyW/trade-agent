from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from ..domain.candle import Candle


@dataclass
class IndicatorSeriesResult:
    name: str

    values: list[Decimal | None]


@dataclass
class IndicatorResult:
    name: str

    type: str

    params: dict[str, Any]

    series: list[IndicatorSeriesResult]


class Indicator(ABC):

    name: str

    type: str = "overlay"

    def validate_period(self, period: int) -> int:

        if period <= 0:
            raise ValueError(
                "period must be greater than 0"
            )

        if period > 1000:
            raise ValueError(
                "period must not exceed 1000"
            )

        return period

    @abstractmethod
    def calculate(
        self,
        candles: list[Candle],
        params: dict[str, Any],
    ) -> IndicatorResult:
        raise NotImplementedError
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from ..domain.candle import Candle
from ..domain.timeframe import AdjustType, KlinePeriod


class MarketRepository(ABC):

    @abstractmethod
    async def get_kline(
        self,
        symbol: str,
        period: KlinePeriod,
        adjust: AdjustType,
        start: date | None,
        end: date | None,
    ) -> list[Candle]:
        raise NotImplementedError
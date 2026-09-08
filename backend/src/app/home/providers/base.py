from abc import ABC, abstractmethod

from ..schemas import (
    HotNewsVO,
    HotSectorVO,
    IndexQuoteVO,
)


class MarketProvider(ABC):

    @abstractmethod
    async def get_indices(self) -> list[IndexQuoteVO]:
        raise NotImplementedError


class NewsProvider(ABC):

    @abstractmethod
    async def get_hot_news(self, limit: int = 10) -> list[HotNewsVO]:
        raise NotImplementedError


class SectorProvider(ABC):

    @abstractmethod
    async def get_hot_sectors(
        self,
        limit: int = 10,
    ) -> list[HotSectorVO]:
        raise NotImplementedError
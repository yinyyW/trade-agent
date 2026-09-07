from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IndexQuote(BaseModel):
    symbol: str
    name: str

    latest_price: float | None = None
    change: float | None = None
    change_percent: float | None = None

    volume: float | None = None
    amount: float | None = None

    updated_at: datetime | None = None


class MarketBreadth(BaseModel):
    up_count: int | None = None
    down_count: int | None = None
    limit_up_count: int | None = None
    limit_down_count: int | None = None


class MarketOverview(BaseModel):
    indices: list[IndexQuote] = Field(default_factory=list)
    breadth: MarketBreadth | None = None


class MacroIndicator(BaseModel):
    name: str
    value: Any | None = None
    unit: str | None = None
    period: str | None = None

    source: str = "同花顺"

    raw_data: Any | None = None


class HomeDashboardData(BaseModel):
    market: MarketOverview
    macro: list[MacroIndicator] = Field(default_factory=list)
    updated_at: datetime


class HomeDashboardResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: HomeDashboardData
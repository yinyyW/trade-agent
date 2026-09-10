from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from .domain.timeframe import AdjustType, KlinePeriod


class IndicatorRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=32,
        description="指标名称，例如 MA、EMA、BOLL"
    )

    params: dict[str, Any] = Field(default_factory=dict)


class MarketKlineRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=32)

    period: KlinePeriod = KlinePeriod.DAY

    adjust: AdjustType = AdjustType.QFQ

    start: date | None = None

    end: date | None = None

    indicators: list[IndicatorRequest] = Field(
        default_factory=list
    )

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def validate_range(self):
        if self.start and self.end and self.start > self.end:
            raise ValueError("start cannot be later than end")

        return self


class IndicatorSeries(BaseModel):
    name: str

    values: list[Decimal | None]


class IndicatorResponse(BaseModel):
    name: str

    type: str

    params: dict[str, Any]

    series: list[IndicatorSeries]


class CandleResponse(BaseModel):
    time: date

    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal

    volume: Decimal
    amount: Decimal

class MarketKlineMeta(BaseModel):
    timezone: str = "Asia/Shanghai"

    currency: str = "CNY"

    price_scale: int = 2


class MarketKlineResponse(BaseModel):
    symbol: str

    name: str | None = None

    period: KlinePeriod

    adjust: AdjustType

    start: date | None = None

    end: date | None = None

    candles: list[CandleResponse]

    indicators: list[IndicatorResponse]

    meta: MarketKlineMeta
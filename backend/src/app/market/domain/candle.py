from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Candle:
    time: date

    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal

    volume: Decimal = Decimal("0")
    amount: Decimal = Decimal("0")

    amplitude: Decimal = Decimal("0")
    change_pct: Decimal = Decimal("0")
    change_amount: Decimal = Decimal("0")
    turnover: Decimal = Decimal("0")

    def is_up(self) -> bool:
        return self.close >= self.open

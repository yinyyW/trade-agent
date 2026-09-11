import asyncio
from datetime import date
from decimal import Decimal

import akshare as ak
from app.market.domain.candle import Candle
from app.market.domain.timeframe import AdjustType, KlinePeriod
from app.market.repository.base import MarketRepository
import pandas as pd
import re


class AkshareMarketRepository(MarketRepository):

    async def get_kline(
        self,
        symbol: str,
        period: KlinePeriod,
        adjust: AdjustType,
        start: date | None,
        end: date | None,
    ) -> list[Candle]:
        start_date = start.strftime("%Y%m%d") if start else None
        end_date = end.strftime("%Y%m%d") if end else None

        # AKShare 是同步 API，放到线程池中执行
        df = await asyncio.to_thread(
            self._get_kline_sync,
            symbol,
            period,
            adjust,
            start=start_date,
            end=end_date,
        )

        if df.empty:
            return []

        return self._convert_to_candles(df)

    def _get_kline_sync(
        self,
        symbol: str,
        period: KlinePeriod,
        adjust: AdjustType,
        start: str | None,
        end: str | None,
    ) -> pd.DataFrame:
        return ak.stock_zh_a_daily(
            symbol=symbol,
            start_date=start,
            end_date=end,
            adjust="qfq",
        )

    @staticmethod
    def _map_period(period: KlinePeriod) -> str:
        mapping = {
            KlinePeriod.DAY: "daily",
            KlinePeriod.WEEK: "weekly",
            KlinePeriod.MONTH: "monthly",
        }

        try:
            return mapping[period]
        except KeyError:
            raise ValueError(f"Unsupported kline period: {period}")

    @staticmethod
    def _map_adjust(adjust: AdjustType) -> str:
        mapping = {
            AdjustType.NONE: "",
            AdjustType.QFQ: "qfq",
            AdjustType.HFQ: "hfq",
        }

        try:
            return mapping[adjust]
        except KeyError:
            raise ValueError(f"Unsupported adjust type: {adjust}")

    @staticmethod
    def _convert_to_candles(df: pd.DataFrame) -> list[Candle]:
        """
        将akshare新浪日线返回的DataFrame转换成Candle对象列表
        :param df: ak.stock_zh_a_daily 返回的dataframe
        :return: list[Candle]
        """
        candles: list[Candle] = []
        pre_close: Decimal | None = None

        for _, row in df.iterrows():
            # 解析日期
            dt = pd.to_datetime(row["date"]).date()

            open_val = Decimal(str(row["open"]))
            high_val = Decimal(str(row["high"]))
            low_val = Decimal(str(row["low"]))
            close_val = Decimal(str(row["close"]))
            volume_val = Decimal(str(row["volume"]))
            amount_val = Decimal(str(row["amount"]))
            turnover_val = Decimal(str(row["turnover"]))

            amplitude = Decimal("0")
            change_pct = Decimal("0")
            change_amount = Decimal("0")

            if pre_close is not None and pre_close > Decimal("0"):
                change_amount = close_val - pre_close
                change_pct = (change_amount / pre_close) * Decimal("100")
                amplitude = ((high_val - low_val) / pre_close) * Decimal("100")

            candle = Candle(
                time=dt,
                open=open_val,
                high=high_val,
                low=low_val,
                close=close_val,
                volume=volume_val,
                amount=amount_val,
                amplitude=amplitude,
                change_pct=change_pct,
                change_amount=change_amount,
                turnover=turnover_val,
            )
            candles.append(candle)
            # 更新前收盘价，用于下一根K线计算
            pre_close = close_val
        return candles
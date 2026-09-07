from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from app.mcp.manager import MCPManager
from .config import HOME_MACRO_METRICS
from .schemas import (
    HomeDashboardData,
    IndexQuote,
    MacroIndicator,
    MarketBreadth,
    MarketOverview,
)

logger = logging.getLogger(__name__)


class HomeService:

    def __init__(self, mcp_manager: MCPManager):
        self.mcp_manager = mcp_manager

    async def get_dashboard(self) -> HomeDashboardData:
        """
        获取首页宏观数据看板。

        数据来源：
        - 指数实时行情：index_highfreq_quotes
        - 宏观经济数据：get_edb_data
        """

        market_task = asyncio.create_task(
            self._get_market_overview()
        )

        macro_task = asyncio.create_task(
            self._get_macro_data()
        )

        market, macro = await asyncio.gather(
            market_task,
            macro_task,
            return_exceptions=True,
        )

        # MCP 某个工具失败不应该导致整个首页失败
        if isinstance(market, Exception):
            logger.exception(
                "Failed to load market dashboard",
                exc_info=market,
            )
            market = MarketOverview()

        if isinstance(macro, Exception):
            logger.exception(
                "Failed to load macro dashboard",
                exc_info=macro,
            )
            macro = []

        return HomeDashboardData(
            market=market,
            macro=macro,
            updated_at=datetime.now(timezone.utc),
        )

    # =========================================================
    # Market
    # =========================================================

    async def _get_market_overview(self) -> MarketOverview:

        tool = self.mcp_manager.get_tool(
            "index_highfreq_quotes"
        )

        if tool is None:
            raise RuntimeError(
                "MCP tool not found: index_highfreq_quotes"
            )

        result = await tool.ainvoke(
            {
                "symbols": (
                    "000001.SH,"
                    "000300.SH,"
                    "399006.SZ"
                ),
                "indicators": (
                    "最新价,"
                    "涨跌,"
                    "涨跌幅,"
                    "成交量,"
                    "成交额,"
                    "上涨家数,"
                    "下跌家数,"
                    "涨停家数,"
                    "跌停家数"
                ),
                "data_mode": "real_time",
            }
        )

        return self._parse_market_result(result)

    # =========================================================
    # Macro
    # =========================================================

    async def _get_macro_data(self) -> list[MacroIndicator]:

        tool = self.mcp_manager.get_tool(
            "get_edb_data"
        )

        if tool is None:
            raise RuntimeError(
                "MCP tool not found: get_edb_data"
            )

        # query = " 查询中国最新GDP、CPI、PPI、制造业PMI、社会融资规模"

        tasks = [
            tool.ainvoke({"query": item.query})
            for item in HOME_MACRO_METRICS
        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        indicators: list[MacroIndicator] = []

        names = [ item.name for item in HOME_MACRO_METRICS ]

        for name, result in zip(names, results):

            if isinstance(result, Exception):
                logger.warning(
                    "Failed to load macro indicator: %s",
                    name,
                    exc_info=result,
                )
                continue

            indicators.append(
                self._parse_macro_result(
                    name=name,
                    result=result,
                )
            )

        return indicators

    # =========================================================
    # Parser
    # =========================================================

    @staticmethod
    def _parse_market_result(
        result: Any,
    ) -> MarketOverview:

        """
        将 MCP 原始结果转换成前端稳定的数据结构。

        注意：
        MCP 返回结构可能随着同花顺 MCP Server 版本变化，
        因此这里集中做适配，不要把 MCP 原始结构直接暴露给前端。
        """

        rows = HomeService._extract_rows(result)

        indices: list[IndexQuote] = []

        breadth = MarketBreadth()

        for row in rows:

            symbol = str(
                row.get("symbol")
                or row.get("代码")
                or ""
            )

            name = str(
                row.get("name")
                or row.get("名称")
                or ""
            )

            quote = IndexQuote(
                symbol=symbol,
                name=name,
                latest_price=HomeService._to_float(
                    row.get("最新价")
                ),
                change=HomeService._to_float(
                    row.get("涨跌")
                ),
                change_percent=HomeService._to_float(
                    row.get("涨跌幅")
                ),
                volume=HomeService._to_float(
                    row.get("成交量")
                ),
                amount=HomeService._to_float(
                    row.get("成交额")
                ),
            )

            indices.append(quote)

            # 市场宽度字段
            if row.get("上涨家数") is not None:
                breadth.up_count = HomeService._to_int(
                    row.get("上涨家数")
                )

            if row.get("下跌家数") is not None:
                breadth.down_count = HomeService._to_int(
                    row.get("下跌家数")
                )

            if row.get("涨停家数") is not None:
                breadth.limit_up_count = HomeService._to_int(
                    row.get("涨停家数")
                )

            if row.get("跌停家数") is not None:
                breadth.limit_down_count = HomeService._to_int(
                    row.get("跌停家数")
                )

        return MarketOverview(
            indices=indices,
            breadth=breadth,
        )

    @staticmethod
    def _parse_macro_result(
        *,
        name: str,
        result: Any,
    ) -> MacroIndicator:

        return MacroIndicator(
            name=name,
            raw_data=result,
        )

    @staticmethod
    def _extract_rows(result: Any) -> list[dict[str, Any]]:

        if result is None:
            return []

        if isinstance(result, list):
            return [
                item
                for item in result
                if isinstance(item, dict)
            ]

        if isinstance(result, dict):

            for key in (
                "data",
                "rows",
                "result",
                "items",
            ):
                value = result.get(key)

                if isinstance(value, list):
                    return [
                        item
                        for item in value
                        if isinstance(item, dict)
                    ]

        return []

    @staticmethod
    def _to_float(value: Any) -> float | None:

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_int(value: Any) -> int | None:

        if value is None:
            return None

        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None
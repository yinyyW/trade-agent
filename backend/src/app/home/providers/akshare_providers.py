from __future__ import annotations

import asyncio
from datetime import datetime
from decimal import Decimal
from http.client import RemoteDisconnected
import logging
from typing import List, Optional
import akshare as ak
import requests
import re
import time
from app.home.schemas import HotNewsVO, HotSectorVO, IndexQuoteVO
from app.home.providers.base import MarketProvider, SectorProvider, NewsProvider

logger = logging.getLogger(__name__)


class AkShareMarketProvider(MarketProvider):

    URL = "https://hq.sinajs.cn/list={}"


    INDEXES = {
        "s_sh000001": "上证指数",
        "s_sz399001": "深证成指",
        "s_sz399006": "创业板指",
    }

    async def get_indices(self) -> list[IndexQuoteVO]:
        return await asyncio.to_thread(
            self._get_indices_sync
        )

    def _get_indices_sync(self) -> list[IndexQuoteVO]:

        symbols = ",".join(self.INDEXES.keys())

        response = requests.get(
            self.URL.format(symbols),
            headers={
                "Referer": "https://finance.sina.com.cn/",
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/131.0 Safari/537.36"
                ),
            },
            timeout=10,
        )

        response.raise_for_status()

        return self._parse_response(
            response.text
        )

    def _parse_response(
        self,
        text: str,
    ) -> list[IndexQuoteVO]:

        result: list[IndexQuoteVO] = []

        for symbol, name in self.INDEXES.items():

            pattern = rf'hq_str_{symbol}="([^"]*)"'
            match = re.search(pattern, text)

            if not match:
                continue

            fields = match.group(1).split(",")

            if len(fields) < 4:
                continue

            try:
                result.append(
                    IndexQuoteVO(
                        code=symbol,
                        name=fields[0] or name,
                        price=Decimal(fields[1]),
                        change=Decimal(fields[2]),
                        change_percent=Decimal(fields[3]),
                        update_time=datetime.now(),
                    )
                )
            except (ValueError, ArithmeticError):
                continue

        return result    

class AkShareSectorProvider(SectorProvider):
    # 必须标记 async！！
    async def get_hot_sectors(self, limit: int = 10) -> List[HotSectorVO]:
        # await to_thread，拿到真实返回值
        res: Optional[List[HotSectorVO]] = await asyncio.to_thread(
            self._fetch_sectors_sync,
            limit=limit
        )
        # 防止返回None，兜底为空列表
        if res is None:
            return []
        return res

    def _fetch_sectors_sync(self, limit: int = 10) -> Optional[List[HotSectorVO]]:
        try:
            df = ak.stock_board_industry_name_ths()
            result: list[HotSectorVO] = [
                HotSectorVO(code=str(row["code"]), name=str(row["name"]))
                for _, row in df.head(limit).iterrows()
            ]
            return result
        except RemoteDisconnected:
            time.sleep(2)
            return None
        except Exception:
            # 捕获其他网络、解析异常
            return None

class AkShareNewsProvider(NewsProvider):
    async def get_hot_news(self, limit: int = 10) -> list[HotNewsVO]:
        """
        获取东财全球财经热点新闻
        dataframe字段：标题、摘要、发布时间、链接
        """
        try:
            result = await asyncio.to_thread(self._fetch_sync, limit)
            return result
        except Exception as e:
            logger.exception("获取热点新闻异常")
            return []

    def _fetch_sync(self, limit: int) -> List[HotNewsVO]:
        max_retry = 2
        for attempt in range(max_retry):
            try:
                df = ak.stock_info_global_em()
                if df is None or df.empty:
                    return []
                df = df.head(limit)
                vo_list: List[HotNewsVO] = []

                for _, row in df.iterrows():
                    # 原始发布时间是字符串，尝试解析；东财示例格式 "2026‑09‑08 14:22:11"
                    pub_str = str(row.get("发布时间", ""))
                    pub_dt: Optional[datetime] = None
                    if pub_str:
                        try:
                            pub_dt = datetime.strptime(pub_str, "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            pass

                    vo = HotNewsVO(
                        title=str(row.get("标题", "")),
                        summary=str(row.get("摘要")) if row.get("摘要") else None,
                        source="东方财富",
                        publish_time=pub_dt,
                        url=str(row.get("链接")) if row.get("链接") else None
                    )
                    vo_list.append(vo)
                return vo_list

            except RemoteDisconnected:
                if attempt < max_retry - 1:
                    time.sleep(1.5)
                    continue
                return []
            except Exception as e:
                logger.warning("新闻抓取单次失败: %s", e)
                return []
        return []
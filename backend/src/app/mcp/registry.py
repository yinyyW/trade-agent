from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable


class ToolDomain(StrEnum):
    """一级业务领域"""

    STOCK = "stock"
    FUND = "fund"
    BOND = "bond"
    GLOBAL_STOCK = "global_stock"
    INDEX = "index"
    SECTOR = "sector"
    FUTURE = "future"
    MACRO = "macro"
    NEWS = "news"
    NOTICE = "notice"


class ToolCapability(StrEnum):
    """二级能力分类"""

    PROFILE = "profile"
    MARKET = "market"
    HIGH_FREQ = "high_freq"
    FINANCIAL = "financial"
    TECHNICAL = "technical"
    RISK = "risk"
    SHAREHOLDER = "shareholder"
    EVENT = "event"
    ESG = "esg"
    OWNERSHIP = "ownership"
    PORTFOLIO = "portfolio"
    COMPANY = "company"
    MACRO = "macro"
    NEWS = "news"
    NOTICE = "notice"
    SEARCH = "search"
    SUMMARY = "summary"


class ToolIntent(StrEnum):
    """
    Agent 场景。

    一个 Intent 可以绑定多个领域/能力。
    """

    STOCK_ANALYSIS = "stock_analysis"
    STOCK_SCREENING = "stock_screening"
    STOCK_QUOTE = "stock_quote"
    STOCK_TECHNICAL = "stock_technical"
    STOCK_FINANCIAL = "stock_financial"
    STOCK_RISK = "stock_risk"
    STOCK_EVENT = "stock_event"

    MARKET_OVERVIEW = "market_overview"
    INDEX_ANALYSIS = "index_analysis"
    SECTOR_ANALYSIS = "sector_analysis"
    MACRO_ANALYSIS = "macro_analysis"

    FUND_ANALYSIS = "fund_analysis"
    BOND_ANALYSIS = "bond_analysis"
    FUTURE_ANALYSIS = "future_analysis"

    GLOBAL_STOCK_ANALYSIS = "global_stock_analysis"

    NEWS_SEARCH = "news_search"
    NOTICE_SEARCH = "notice_search"


@dataclass(frozen=True, slots=True)
class MCPToolDefinition:
    """
    MCP Tool 元数据。

    注意：
    这里不保存 Tool 实例，只保存 Tool 的业务描述。
    真正的 Tool 实例由 MCP Server 动态返回。
    """

    name: str
    domain: ToolDomain
    capability: ToolCapability
    intents: frozenset[ToolIntent]

    description: str = ""

    # 是否只读。
    # 当前同花顺 MCP Tools 全部属于查询类工具，因此默认 True。
    read_only: bool = True


# ============================================================
# MCP Tool Registry
# ============================================================

TOOL_DEFINITIONS: tuple[MCPToolDefinition, ...] = (

    # ========================================================
    # A 股
    # ========================================================

    MCPToolDefinition(
        name="get_stock_summary",
        domain=ToolDomain.STOCK,
        capability=ToolCapability.SUMMARY,
        intents=frozenset({
            ToolIntent.STOCK_ANALYSIS,
            ToolIntent.STOCK_QUOTE,
            ToolIntent.STOCK_FINANCIAL,
        }),
        description="A股股票数据信息摘要。",
    ),

    MCPToolDefinition(
        name="search_stocks",
        domain=ToolDomain.STOCK,
        capability=ToolCapability.SEARCH,
        intents=frozenset({
            ToolIntent.STOCK_SCREENING,
        }),
        description="根据自然语言条件智能选股。",
    ),

    MCPToolDefinition(
        name="get_stock_performance",
        domain=ToolDomain.STOCK,
        capability=ToolCapability.TECHNICAL,
        intents=frozenset({
            ToolIntent.STOCK_ANALYSIS,
            ToolIntent.STOCK_TECHNICAL,
            ToolIntent.STOCK_QUOTE,
        }),
        description="A股日频历史行情、技术指标和技术形态。",
    ),

    MCPToolDefinition(
        name="get_stock_info",
        domain=ToolDomain.STOCK,
        capability=ToolCapability.PROFILE,
        intents=frozenset({
            ToolIntent.STOCK_ANALYSIS,
            ToolIntent.STOCK_SCREENING,
        }),
        description="A股股票及上市公司基本资料。",
    ),

    MCPToolDefinition(
        name="get_stock_shareholders",
        domain=ToolDomain.STOCK,
        capability=ToolCapability.SHAREHOLDER,
        intents=frozenset({
            ToolIntent.STOCK_ANALYSIS,
        }),
        description="股票股本结构与股东结构。",
    ),

    MCPToolDefinition(
        name="get_stock_financials",
        domain=ToolDomain.STOCK,
        capability=ToolCapability.FINANCIAL,
        intents=frozenset({
            ToolIntent.STOCK_ANALYSIS,
            ToolIntent.STOCK_FINANCIAL,
        }),
        description="A股财务报表、财务指标和估值数据。",
    ),

    MCPToolDefinition(
        name="get_risk_indicators",
        domain=ToolDomain.STOCK,
        capability=ToolCapability.RISK,
        intents=frozenset({
            ToolIntent.STOCK_ANALYSIS,
            ToolIntent.STOCK_RISK,
        }),
        description="A股定量风险指标，如 Alpha、Beta、波动率、夏普比率、VaR。",
    ),

    MCPToolDefinition(
        name="get_stock_events",
        domain=ToolDomain.STOCK,
        capability=ToolCapability.EVENT,
        intents=frozenset({
            ToolIntent.STOCK_ANALYSIS,
            ToolIntent.STOCK_EVENT,
        }),
        description="A股上市公司公开披露事件。",
    ),

    MCPToolDefinition(
        name="get_esg_data",
        domain=ToolDomain.STOCK,
        capability=ToolCapability.ESG,
        intents=frozenset({
            ToolIntent.STOCK_ANALYSIS,
        }),
        description="A股上市公司ESG评级与报告数据。",
    ),

    MCPToolDefinition(
        name="stock_highfreq_quotes",
        domain=ToolDomain.STOCK,
        capability=ToolCapability.HIGH_FREQ,
        intents=frozenset({
            ToolIntent.STOCK_QUOTE,
            ToolIntent.MARKET_OVERVIEW,
        }),
        description="A股实时快照与日内高频行情。",
    ),

    # ========================================================
    # 基金
    # ========================================================

    MCPToolDefinition(
        name="get_fund_profile",
        domain=ToolDomain.FUND,
        capability=ToolCapability.PROFILE,
        intents=frozenset({
            ToolIntent.FUND_ANALYSIS,
        }),
        description="基金基本资料及发行信息。",
    ),

    MCPToolDefinition(
        name="get_fund_market_performance",
        domain=ToolDomain.FUND,
        capability=ToolCapability.MARKET,
        intents=frozenset({
            ToolIntent.FUND_ANALYSIS,
        }),
        description="基金行情、业绩和绩效评价指标。",
    ),

    MCPToolDefinition(
        name="get_fund_ownership",
        domain=ToolDomain.FUND,
        capability=ToolCapability.OWNERSHIP,
        intents=frozenset({
            ToolIntent.FUND_ANALYSIS,
        }),
        description="基金份额及持有人结构。",
    ),

    MCPToolDefinition(
        name="get_fund_portfolio",
        domain=ToolDomain.FUND,
        capability=ToolCapability.PORTFOLIO,
        intents=frozenset({
            ToolIntent.FUND_ANALYSIS,
        }),
        description="基金资产配置、行业分布和持仓明细。",
    ),

    MCPToolDefinition(
        name="get_fund_financials",
        domain=ToolDomain.FUND,
        capability=ToolCapability.FINANCIAL,
        intents=frozenset({
            ToolIntent.FUND_ANALYSIS,
        }),
        description="基金报告期财务数据及分红信息。",
    ),

    MCPToolDefinition(
        name="get_fund_company_info",
        domain=ToolDomain.FUND,
        capability=ToolCapability.COMPANY,
        intents=frozenset({
            ToolIntent.FUND_ANALYSIS,
        }),
        description="基金公司基本信息、资管规模、基金经理及业绩指标。",
    ),

    MCPToolDefinition(
        name="fund_highfreq_quotes",
        domain=ToolDomain.FUND,
        capability=ToolCapability.HIGH_FREQ,
        intents=frozenset({
            ToolIntent.FUND_ANALYSIS,
        }),
        description="公募基金实时快照与日内高频行情。",
    ),

    # ========================================================
    # 宏观经济
    # ========================================================

    MCPToolDefinition(
        name="get_edb_data",
        domain=ToolDomain.MACRO,
        capability=ToolCapability.MACRO,
        intents=frozenset({
            ToolIntent.MACRO_ANALYSIS,
            ToolIntent.MARKET_OVERVIEW,
        }),
        description="全球、中国、区域、行业及大宗商品宏观经济指标。",
    ),

    # ========================================================
    # 新闻 / 公告
    # ========================================================

    MCPToolDefinition(
        name="search_news",
        domain=ToolDomain.NEWS,
        capability=ToolCapability.NEWS,
        intents=frozenset({
            ToolIntent.NEWS_SEARCH,
            ToolIntent.STOCK_ANALYSIS,
            ToolIntent.MARKET_OVERVIEW,
        }),
        description="同花顺财经新闻资讯检索。",
    ),

    MCPToolDefinition(
        name="search_notice",
        domain=ToolDomain.NOTICE,
        capability=ToolCapability.NOTICE,
        intents=frozenset({
            ToolIntent.NOTICE_SEARCH,
            ToolIntent.STOCK_ANALYSIS,
            ToolIntent.STOCK_EVENT,
        }),
        description="A股、基金、港美股公告内容语义检索。",
    ),

    # ========================================================
    # 债券
    # ========================================================

    MCPToolDefinition(
        name="bond_basic_info",
        domain=ToolDomain.BOND,
        capability=ToolCapability.PROFILE,
        intents=frozenset({
            ToolIntent.BOND_ANALYSIS,
        }),
        description="债券基本信息及发行兑付信息。",
    ),

    MCPToolDefinition(
        name="bond_market_data",
        domain=ToolDomain.BOND,
        capability=ToolCapability.MARKET,
        intents=frozenset({
            ToolIntent.BOND_ANALYSIS,
        }),
        description="债券行情、估值、久期、凸性等数据。",
    ),

    MCPToolDefinition(
        name="bond_financial_data",
        domain=ToolDomain.BOND,
        capability=ToolCapability.FINANCIAL,
        intents=frozenset({
            ToolIntent.BOND_ANALYSIS,
        }),
        description="债券发行主体财务数据及财务分析指标。",
    ),

    MCPToolDefinition(
        name="bond_special_data",
        domain=ToolDomain.BOND,
        capability=ToolCapability.EVENT,
        intents=frozenset({
            ToolIntent.BOND_ANALYSIS,
        }),
        description="信用评级、回购、可转债转股等特殊债券数据。",
    ),

    MCPToolDefinition(
        name="bond_highfreq_quotes",
        domain=ToolDomain.BOND,
        capability=ToolCapability.HIGH_FREQ,
        intents=frozenset({
            ToolIntent.BOND_ANALYSIS,
        }),
        description="交易所债券实时快照及日内高频行情。",
    ),

    # ========================================================
    # 港美股
    # ========================================================

    MCPToolDefinition(
        name="global_stock_profile",
        domain=ToolDomain.GLOBAL_STOCK,
        capability=ToolCapability.PROFILE,
        intents=frozenset({
            ToolIntent.GLOBAL_STOCK_ANALYSIS,
        }),
        description="港美股证券及上市公司基本资料。",
    ),

    MCPToolDefinition(
        name="global_stock_quotes",
        domain=ToolDomain.GLOBAL_STOCK,
        capability=ToolCapability.MARKET,
        intents=frozenset({
            ToolIntent.GLOBAL_STOCK_ANALYSIS,
        }),
        description="港美股行情、技术指标、技术形态及风险指标。",
    ),

    MCPToolDefinition(
        name="global_stock_financial",
        domain=ToolDomain.GLOBAL_STOCK,
        capability=ToolCapability.FINANCIAL,
        intents=frozenset({
            ToolIntent.GLOBAL_STOCK_ANALYSIS,
        }),
        description="港美股财务数据、财务指标、估值和盈利预测。",
    ),

    MCPToolDefinition(
        name="global_stock_events",
        domain=ToolDomain.GLOBAL_STOCK,
        capability=ToolCapability.EVENT,
        intents=frozenset({
            ToolIntent.GLOBAL_STOCK_ANALYSIS,
        }),
        description="港美股IPO、回购、分红、ESG等事件。",
    ),

    # ========================================================
    # 指数
    # ========================================================

    MCPToolDefinition(
        name="index_data",
        domain=ToolDomain.INDEX,
        capability=ToolCapability.MARKET,
        intents=frozenset({
            ToolIntent.INDEX_ANALYSIS,
            ToolIntent.MARKET_OVERVIEW,
        }),
        description="股票、基金、债券、期货及ESG指数数据。",
    ),

    MCPToolDefinition(
        name="index_highfreq_quotes",
        domain=ToolDomain.INDEX,
        capability=ToolCapability.HIGH_FREQ,
        intents=frozenset({
            ToolIntent.INDEX_ANALYSIS,
            ToolIntent.MARKET_OVERVIEW,
        }),
        description="指数实时快照与日内高频行情。",
    ),

    # ========================================================
    # 板块
    # ========================================================

    MCPToolDefinition(
        name="sector_data",
        domain=ToolDomain.SECTOR,
        capability=ToolCapability.MARKET,
        intents=frozenset({
            ToolIntent.SECTOR_ANALYSIS,
            ToolIntent.MARKET_OVERVIEW,
        }),
        description="行业、概念及市场分类板块数据。",
    ),

    # ========================================================
    # 期货
    # ========================================================

    MCPToolDefinition(
        name="future_profile",
        domain=ToolDomain.FUTURE,
        capability=ToolCapability.PROFILE,
        intents=frozenset({
            ToolIntent.FUTURE_ANALYSIS,
        }),
        description="期货合约及标的基本资料。",
    ),

    MCPToolDefinition(
        name="future_quotes",
        domain=ToolDomain.FUTURE,
        capability=ToolCapability.MARKET,
        intents=frozenset({
            ToolIntent.FUTURE_ANALYSIS,
        }),
        description="期货行情、技术指标、技术形态和持仓指标。",
    ),
)


# ============================================================
# Registry
# ============================================================

class MCPToolRegistry:
    """
    MCP Tool Registry。

    负责：
    1. Tool 元数据管理
    2. 根据 domain 查询
    3. 根据 capability 查询
    4. 根据 Agent intent 查询
    5. 将真实 MCP Tool 映射成 Agent 可使用的 Tool
    """

    def __init__(
        self,
        definitions: Iterable[MCPToolDefinition] = TOOL_DEFINITIONS,
    ):
        self._definitions = tuple(definitions)

        self._by_name = {
            item.name: item
            for item in self._definitions
        }

    # --------------------------------------------------------
    # 基础查询
    # --------------------------------------------------------

    def get_definition(
        self,
        name: str,
    ) -> MCPToolDefinition | None:
        return self._by_name.get(name)

    def get_definitions(self) -> tuple[MCPToolDefinition, ...]:
        return self._definitions

    # --------------------------------------------------------
    # 按 Domain
    # --------------------------------------------------------

    def get_by_domain(
        self,
        domain: ToolDomain,
    ) -> list[MCPToolDefinition]:

        return [
            item
            for item in self._definitions
            if item.domain == domain
        ]

    # --------------------------------------------------------
    # 按 Capability
    # --------------------------------------------------------

    def get_by_capability(
        self,
        capability: ToolCapability,
    ) -> list[MCPToolDefinition]:

        return [
            item
            for item in self._definitions
            if item.capability == capability
        ]

    # --------------------------------------------------------
    # 按 Intent
    # --------------------------------------------------------

    def get_by_intent(
        self,
        intent: ToolIntent,
    ) -> list[MCPToolDefinition]:

        return [
            item
            for item in self._definitions
            if intent in item.intents
        ]

    # --------------------------------------------------------
    # 多条件
    # --------------------------------------------------------

    def get(
        self,
        *,
        domains: Iterable[ToolDomain] | None = None,
        capabilities: Iterable[ToolCapability] | None = None,
        intents: Iterable[ToolIntent] | None = None,
    ) -> list[MCPToolDefinition]:

        domain_set = set(domains or [])
        capability_set = set(capabilities or [])
        intent_set = set(intents or [])

        result = []

        for item in self._definitions:

            if domain_set and item.domain not in domain_set:
                continue

            if (
                capability_set
                and item.capability not in capability_set
            ):
                continue

            if (
                intent_set
                and not item.intents.intersection(intent_set)
            ):
                continue

            result.append(item)

        return result

    # --------------------------------------------------------
    # 将 Registry Definition 映射为真实 MCP Tool
    # --------------------------------------------------------

    def filter_tools(
        self,
        tools: Iterable,
        *,
        domains: Iterable[ToolDomain] | None = None,
        capabilities: Iterable[ToolCapability] | None = None,
        intents: Iterable[ToolIntent] | None = None,
    ) -> list:

        definitions = self.get(
            domains=domains,
            capabilities=capabilities,
            intents=intents,
        )

        allowed_names = {
            item.name
            for item in definitions
        }

        return [
            tool
            for tool in tools
            if tool.name in allowed_names
        ]
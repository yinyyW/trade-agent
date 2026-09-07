from dataclasses import dataclass


@dataclass(frozen=True)
class MacroMetricConfig:
    key: str
    name: str
    query: str


HOME_MACRO_METRICS = (
    MacroMetricConfig(
        key="gdp",
        name="GDP",
        query="中国GDP最新数据",
    ),
    MacroMetricConfig(
        key="cpi",
        name="CPI",
        query="中国CPI最新数据",
    ),
    MacroMetricConfig(
        key="ppi",
        name="PPI",
        query="中国PPI最新数据",
    ),
    MacroMetricConfig(
        key="pmi",
        name="制造业PMI",
        query="中国制造业PMI最新数据",
    ),
    MacroMetricConfig(
        key="social_financing",
        name="社会融资规模",
        query="中国社会融资规模最新数据",
    ),
)
from enum import StrEnum


class KlinePeriod(StrEnum):
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1m"


class AdjustType(StrEnum):
    NONE = "none"
    QFQ = "qfq"
    HFQ = "hfq"
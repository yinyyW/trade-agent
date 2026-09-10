from .base import Indicator
from .ma import MAIndicator
from .ema import EMAIndicator
from .boll import BOLLIndicator


INDICATOR_REGISTRY: dict[str, Indicator] = {
    "MA": MAIndicator(),
    "EMA": EMAIndicator(),
    "BOLL": BOLLIndicator(),
}
"""
Homepage module.

包含：
- 首页宏观数据看板
- 市场指数实时行情
- 宏观经济指标
"""

from .router import router
from .service import HomeService

__all__ = [
    "HomeService",
    "router",
]
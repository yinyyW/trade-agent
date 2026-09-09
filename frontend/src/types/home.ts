/**
 * 首页看板相关类型定义。
 *
 * 字段与后端 backend/src/app/home/schemas.py 中的 HomeDashboardVO 保持一致。
 * 后端 Decimal 字段在 JSON 序列化时可能以数字或字符串返回，因此统一放宽为
 * number | string，由前端格式化工具统一处理。
 */

/** 通用接口响应包裹结构 */
export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

/** 指数实时行情 */
export interface IndexQuoteVO {
  code: string;
  name: string;
  /** 最新价 */
  price: number | string;
  /** 涨跌额 */
  change: number | string;
  /** 涨跌幅（%） */
  change_percent: number | string;
  update_time?: string | null;
}

/** 市场速览数据 */
export interface MarketOverviewVO {
  indices: IndexQuoteVO[];
}

/** 热点新闻 */
export interface HotNewsVO {
  title: string;
  summary?: string | null;
  source?: string | null;
  publish_time?: string | null;
  url?: string | null;
}

/**
 * 热门行业。
 *
 * 当前后端接口仅稳定返回 code / name，涨幅、资金流等字段暂未接入。
 * 首页只展示行业名称。
 */
export interface HotSectorVO {
  code: string;
  name: string;
}

/** 首页看板聚合数据 */
export interface HomeDashboardVO {
  update_time: string;
  market: MarketOverviewVO;
  news: HotNewsVO[];
  sectors: HotSectorVO[];
}

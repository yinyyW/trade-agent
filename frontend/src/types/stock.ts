export type KlinePeriod = "1d" | "1w" | "1m";

export type AdjustType = "none" | "qfq" | "hfq";

export interface Candle {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount: number;
}

export interface IndicatorSeries {
  name: string;
  values: Array<number | null>;
}

export interface IndicatorResponse {
  name: string;
  type: "overlay" | "subchart";
  params: Record<string, unknown>;
  series: IndicatorSeries[];
}

export interface MarketKlineResponse {
  symbol: string;
  name?: string;

  period: KlinePeriod;
  adjust: AdjustType;

  start?: string;
  end?: string;

  candles: Candle[];

  indicators: IndicatorResponse[];

  meta: {
    timezone: string;
    currency: string;
    price_scale: number;
  };
}

export interface IndicatorRequest {
  name: string;
  params?: Record<string, unknown>;
}

export interface MarketKlineRequest {
  symbol: string;
  period: KlinePeriod;
  adjust: AdjustType;
  start?: string;
  end?: string;
  indicators?: IndicatorRequest[];
}

/**
 * 个股详情页顶部行情摘要。
 *
 * 当前后端仅提供 K 线接口，因此价格、涨跌、今开、最高、最低均由
 * 最近两根 K 线推导；换手率暂未由接口返回。
 */
export interface StockQuoteSummary {
  /** 原始行情标识，例如 sh600519。 */
  symbol: string;
  /** 展示用代码，例如 600519.SH。 */
  code: string;
  /** 股票名称，接口未返回时为 null。 */
  name: string | null;
  /** 最新价。 */
  price: number;
  /** 涨跌额。 */
  change: number;
  /** 涨跌幅（%）。 */
  changePercent: number;
  /** 今开。 */
  open: number;
  /** 最高。 */
  high: number;
  /** 最低。 */
  low: number;
  /** 换手率（%），接口未返回时为 null。 */
  turnover: number | null;
}

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

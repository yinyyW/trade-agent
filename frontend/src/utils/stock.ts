import type { MarketKlineResponse, StockQuoteSummary } from "../types/stock";

/** 路由未携带有效股票代码时使用的默认标的。 */
export const DEFAULT_STOCK_SYMBOL = "sh600519";

/**
 * 将路由参数标准化为后端行情标识。
 *
 * 支持 sh600519 / sz000001 这类完整标识，也支持 600519 / 000001
 * 这类 6 位代码；上海代码以 6/9 开头，其余按深圳代码处理。
 */
export function normalizeStockSymbol(value?: string): string {
  const trimmed = value?.trim().toLowerCase() ?? "";

  if (/^(sh|sz|bj)\d{6}$/.test(trimmed)) {
    return trimmed;
  }

  if (/^\d{6}$/.test(trimmed)) {
    return trimmed.startsWith("6") || trimmed.startsWith("9")
      ? `sh${trimmed}`
      : `sz${trimmed}`;
  }

  return DEFAULT_STOCK_SYMBOL;
}

/** 将 sh600519 转换为 600519.SH 展示格式。 */
export function formatStockCode(symbol: string): string {
  const match = /^(sh|sz|bj)(\d{6})$/i.exec(symbol);
  if (!match) {
    return symbol;
  }
  return `${match[2]}.${match[1].toUpperCase()}`;
}

/**
 * 从 K 线数据推导详情页顶部行情摘要。
 *
 * 后端当前仅提供 K 线数据，最新价、涨跌、今开、最高、最低均由最近
 * 两根 K 线计算；换手率暂未返回。
 */
export function buildStockQuoteSummary(
  kline: MarketKlineResponse,
): StockQuoteSummary | null {
  const { candles } = kline;
  if (candles.length === 0) {
    return null;
  }

  const latest = candles[candles.length - 1];
  const previous = candles.length > 1 ? candles[candles.length - 2] : null;
  const previousClose = previous ? previous.close : latest.open;
  const change = latest.close - previousClose;
  const changePercent =
    previousClose !== 0 ? (change / previousClose) * 100 : 0;

  return {
    symbol: kline.symbol,
    code: formatStockCode(kline.symbol),
    name: kline.name?.trim() || null,
    price: latest.close,
    change,
    changePercent,
    open: latest.open,
    high: latest.high,
    low: latest.low,
    turnover: null,
  };
}

/** A 股红涨绿跌趋势样式。 */
export function getStockTrendClass(
  value: number,
): "up" | "down" | "flat" {
  if (value > 0) {
    return "up";
  }
  if (value < 0) {
    return "down";
  }
  return "flat";
}

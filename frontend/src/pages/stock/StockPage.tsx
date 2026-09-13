import { useCallback, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Empty } from "antd";
import { fetchMarketKline } from "@/api/stock";
import { getErrorMessage } from "@/api/http";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/common/Status";
import KLineChart from "@/components/market/KLineChart";
import type {
  KLineChartDirection,
  KLineChartPayload,
} from "@/components/market/KLineChart";
import StockHeader from "@/components/market/StockHeader";
import StockSummaryAside from "@/components/market/StockSummaryAside";
import type {
  AdjustType,
  Candle,
  IndicatorResponse,
  KlinePeriod,
  MarketKlineResponse,
} from "@/types/stock";
import { buildStockQuoteSummary, normalizeStockSymbol } from "@/utils/stock";
import "@/styles/stock.css";

type StockTabKey = "trend" | "finance" | "score";

const STOCK_TABS: Array<{ key: StockTabKey; label: string }> = [
  { key: "trend", label: "走势分析" },
  { key: "finance", label: "财报解读" },
  { key: "score", label: "综合评价" },
];

/** 详情页当前只使用日线前复权数据，周期切换在此扩展即可。 */
const KLINE_PERIOD: KlinePeriod = "1d";
const KLINE_ADJUST: AdjustType = "qfq";
const MA_PERIODS: number[] = [5, 10, 20];

/** 初始加载区间 = 视口可容纳的 K 线数量 × 该倍数。 */
const OVERSCAN_RATIO = 3;
/** 滚动加载区间 = 视口可容纳的 K 线数量 × 该倍数。 */
const PREFETCH_RATIO = 2;
const MIN_BATCH_BARS = 60;
const MAX_BATCH_BARS = 500;
/** 日线一年约 250 个交易日，按此比例把 K 线根数换算成自然日跨度。 */
const TRADING_TO_CALENDAR_RATIO = 1.6;
const CALENDAR_PADDING_DAYS = 10;
/** 均线预热区间：每次多取一段数据，避免窗口开头的 MA 为 null。 */
const MA_WARMUP_BARS = 60;
const EARLIEST_SUPPORTED_DATE = "1990-01-01";

const DEFAULT_META: MarketKlineResponse["meta"] = {
  timezone: "Asia/Shanghai",
  currency: "CNY",
  price_scale: 100,
};

const EMPTY_PAYLOAD: KLineChartPayload = { candles: [], indicators: [] };

interface DateRange {
  start: string;
  end: string;
}

interface IndicatorStoreEntry {
  type: IndicatorResponse["type"];
  params: Record<string, unknown>;
  series: Map<string, Map<string, number | null>>;
}

function formatDateForApi(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function parseDateForApi(value: string): Date {
  const [year, month, day] = value.split("-").map(Number);
  return new Date(year, month - 1, day);
}

function addCalendarDays(value: string, days: number): string {
  const date = parseDateForApi(value);
  date.setDate(date.getDate() + days);
  return formatDateForApi(date);
}

function barsToCalendarDays(bars: number): number {
  return Math.ceil(bars * TRADING_TO_CALENDAR_RATIO) + CALENDAR_PADDING_DAYS;
}

function clampBatchBars(bars: number): number {
  return Math.min(MAX_BATCH_BARS, Math.max(MIN_BATCH_BARS, Math.round(bars)));
}

function todayString(): string {
  return formatDateForApi(new Date());
}

/**
 * 个股分析详情页。
 *
 * 股票代码通过 /stock/:symbol 路由参数进入，K 线数据按视口分片加载：
 * 1. 图表挂载后上报一屏可容纳的 K 线数量，据此决定初始时间区间；
 * 2. 用户拖动到数据边缘时，按方向加载相邻的日期区间；
 * 3. 已加载区间与 K 线、指标值均缓存在前端，重复区间不再发起请求；
 * 4. 同一时刻只允许一个请求在途，loading 期间的新请求排队等待。
 *
 * 财报与综合评价依赖的 AI 接口暂未接入，因此只保留对应 Tab 的空状态。
 */
export default function StockPage() {
  const { symbol: routeSymbol } = useParams<{ symbol: string }>();
  const navigate = useNavigate();
  const symbol = normalizeStockSymbol(routeSymbol);

  const [payload, setPayload] = useState<KLineChartPayload>(EMPTY_PAYLOAD);
  const [stockName, setStockName] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [firstLoadDone, setFirstLoadDone] = useState(false);
  const [hasMoreBefore, setHasMoreBefore] = useState(true);
  const [hasMoreAfter, setHasMoreAfter] = useState(false);
  const [activeTab, setActiveTab] = useState<StockTabKey>("trend");
  const [watched, setWatched] = useState(false);

  const symbolRef = useRef(symbol);
  symbolRef.current = symbol;

  /** K 线与指标缓存，key 为 YYYY-MM-DD。 */
  const candleMapRef = useRef<Map<string, Candle>>(new Map());
  const orderedTimesRef = useRef<string[]>([]);
  const indicatorStoreRef = useRef<Map<string, IndicatorStoreEntry>>(new Map());
  /** 已请求过的日期区间，用于避免重复请求。 */
  const coveredRangesRef = useRef<DateRange[]>([]);

  /** 请求调度：runningRef 保证同一时刻只有一个请求在途。 */
  const sessionIdRef = useRef(0);
  const runningRef = useRef(false);
  const pendingRef = useRef<{ before: boolean; after: boolean }>({
    before: false,
    after: false,
  });
  const pendingInitialRef = useRef(false);
  const exhaustedRef = useRef({ before: false, after: false });

  const viewportBarsRef = useRef(0);
  const initialViewportRef = useRef<number | null>(null);
  const metaRef = useRef<MarketKlineResponse["meta"]>(DEFAULT_META);

  // 股票代码变化时同步重置缓存与状态（渲染期重置，避免与图表挂载副作用产生竞态）。
  const [sessionSymbol, setSessionSymbol] = useState(symbol);
  if (sessionSymbol !== symbol) {
    setSessionSymbol(symbol);
    sessionIdRef.current += 1;
    candleMapRef.current = new Map();
    orderedTimesRef.current = [];
    indicatorStoreRef.current = new Map();
    coveredRangesRef.current = [];
    pendingRef.current = { before: false, after: false };
    pendingInitialRef.current = false;
    exhaustedRef.current = { before: false, after: false };
    viewportBarsRef.current = 0;
    initialViewportRef.current = null;
    metaRef.current = DEFAULT_META;
    setPayload(EMPTY_PAYLOAD);
    setStockName(null);
    setLoading(false);
    setError(null);
    setFirstLoadDone(false);
    setHasMoreBefore(true);
    setHasMoreAfter(false);
    setActiveTab("trend");
    setWatched(false);
  }

  const rebuildPayload = useCallback(() => {
    const times = Array.from(candleMapRef.current.keys()).sort();
    orderedTimesRef.current = times;
    const candles = times.map(
      (time) => candleMapRef.current.get(time) as Candle,
    );

    const indicators: IndicatorResponse[] = [];
    indicatorStoreRef.current.forEach((entry, name) => {
      indicators.push({
        name,
        type: entry.type,
        params: entry.params,
        series: Array.from(entry.series.entries()).map(
          ([seriesName, valuesByTime]) => ({
            name: seriesName,
            values: times.map((time) => valuesByTime.get(time) ?? null),
          }),
        ),
      });
    });

    setPayload({ candles, indicators });
  }, []);

  const syncHasMore = useCallback(() => {
    const times = orderedTimesRef.current;
    const latest = times.length > 0 ? times[times.length - 1] : null;
    setHasMoreBefore(!exhaustedRef.current.before);
    setHasMoreAfter(
      !exhaustedRef.current.after && latest !== null && latest < todayString(),
    );
  }, []);

  /** 把一次响应合并进缓存，返回新增的 K 线根数。 */
  const mergeResponse = useCallback(
    (response: MarketKlineResponse, fromTime: string) => {
      const seriesPlan: Array<{
        valuesByTime: Map<string, number | null>;
        values: Array<number | null>;
      }> = [];

      response.indicators.forEach((indicator) => {
        let entry = indicatorStoreRef.current.get(indicator.name);
        if (!entry) {
          entry = {
            type: indicator.type,
            params: indicator.params,
            series: new Map(),
          };
          indicatorStoreRef.current.set(indicator.name, entry);
        }
        indicator.series.forEach((series) => {
          let valuesByTime = entry.series.get(series.name);
          if (!valuesByTime) {
            valuesByTime = new Map();
            entry.series.set(series.name, valuesByTime);
          }
          seriesPlan.push({ valuesByTime, values: series.values });
        });
      });

      let added = 0;
      response.candles.forEach((candle, index) => {
        const time = String(candle.time);
        if (time < fromTime) {
          // 均线预热区只用于指标计算，不进入前端缓存。
          return;
        }
        if (!candleMapRef.current.has(time)) {
          added += 1;
        }
        candleMapRef.current.set(time, candle);
        seriesPlan.forEach(({ valuesByTime, values }) => {
          valuesByTime.set(time, values[index] ?? null);
        });
      });

      return added;
    },
    [],
  );

  const fetchRange = useCallback(
    async (range: DateRange) => {
      const sessionId = sessionIdRef.current;
      const start =
        range.start < EARLIEST_SUPPORTED_DATE
          ? EARLIEST_SUPPORTED_DATE
          : range.start;
      const warmupStart = addCalendarDays(
        start,
        -barsToCalendarDays(MA_WARMUP_BARS),
      );

      const response = await fetchMarketKline({
        symbol: symbolRef.current,
        period: KLINE_PERIOD,
        adjust: KLINE_ADJUST,
        start: warmupStart,
        end: range.end,
        indicators: [{ name: "MA", params: { periods: MA_PERIODS } }],
      });

      if (sessionId !== sessionIdRef.current) {
        // 已切换股票，丢弃过期响应。
        return 0;
      }

      coveredRangesRef.current.push({ start, end: range.end });
      const added = mergeResponse(response, start);
      rebuildPayload();
      setError(null);

      if (response.name?.trim()) {
        setStockName(response.name.trim());
      }
      if (response.meta) {
        metaRef.current = response.meta;
      }
      if (start <= EARLIEST_SUPPORTED_DATE) {
        exhaustedRef.current.before = true;
      }
      if (range.end >= todayString()) {
        // 区间已覆盖到今天，说明之后不会再有更新的 K 线。
        exhaustedRef.current.after = true;
      }

      return added;
    },
    [mergeResponse, rebuildPayload],
  );

  const isRangeLoaded = useCallback(
    (range: DateRange) =>
      coveredRangesRef.current.some(
        (covered) =>
          covered.start <= range.start && covered.end >= range.end,
      ),
    [],
  );

  /** 按加载方向推算下一个日期区间；返回 null 表示该方向已无更多数据。 */
  const prepareRange = useCallback(
    (direction: KLineChartDirection): DateRange | null => {
      const times = orderedTimesRef.current;
      const today = todayString();
      const batchDays = barsToCalendarDays(
        clampBatchBars(viewportBarsRef.current * PREFETCH_RATIO),
      );

      if (times.length === 0) {
        if (direction === "after") {
          return null;
        }
        const initialBars = clampBatchBars(
          viewportBarsRef.current * OVERSCAN_RATIO,
        );
        return {
          start: addCalendarDays(today, -barsToCalendarDays(initialBars)),
          end: today,
        };
      }

      if (direction === "before") {
        const earliest = times[0];
        if (earliest <= EARLIEST_SUPPORTED_DATE) {
          return null;
        }
        const end = addCalendarDays(earliest, -1);
        const start = addCalendarDays(end, -batchDays);
        return {
          start: start < EARLIEST_SUPPORTED_DATE ? EARLIEST_SUPPORTED_DATE : start,
          end,
        };
      }

      const latest = times[times.length - 1];
      if (latest >= today) {
        return null;
      }
      const start = addCalendarDays(latest, 1);
      if (start > today) {
        return null;
      }
      const end = addCalendarDays(start, batchDays);
      return { start, end: end > today ? today : end };
    },
    [],
  );

  /** 串行执行加载队列，保证同一时刻只有一个请求在途。 */
  const runLoader = useCallback(async () => {
    if (runningRef.current) {
      return;
    }
    runningRef.current = true;
    setLoading(true);

    try {
      while (pendingRef.current.before || pendingRef.current.after) {
        const direction: KLineChartDirection = pendingRef.current.before
          ? "before"
          : "after";
        const isInitialRequest = pendingInitialRef.current;
        pendingRef.current[direction] = false;
        pendingInitialRef.current = false;

        const range = exhaustedRef.current[direction]
          ? null
          : prepareRange(direction);
        if (!range) {
          exhaustedRef.current[direction] = true;
          if (isInitialRequest) {
            setFirstLoadDone(true);
          }
          continue;
        }
        if (isRangeLoaded(range)) {
          // 命中缓存，不再重复请求。
          if (isInitialRequest) {
            setFirstLoadDone(true);
          }
          continue;
        }

        try {
          const added = await fetchRange(range);
          if (added === 0) {
            exhaustedRef.current[direction] = true;
          }
        } catch (requestError) {
          setError(getErrorMessage(requestError));
        } finally {
          if (isInitialRequest) {
            setFirstLoadDone(true);
          }
          syncHasMore();
        }
      }
    } finally {
      runningRef.current = false;
      setLoading(false);
      syncHasMore();
    }
  }, [fetchRange, isRangeLoaded, prepareRange, syncHasMore]);

  /** 图表上报首屏可容纳的 K 线数量后，按视口决定初始加载区间。 */
  const handleInitialViewport = useCallback(
    (visibleBars: number) => {
      if (initialViewportRef.current !== null) {
        return;
      }
      initialViewportRef.current = visibleBars;
      viewportBarsRef.current = visibleBars;
      pendingInitialRef.current = true;
      pendingRef.current.before = true;
      void runLoader();
    },
    [runLoader],
  );

  /** 图表拖动到数据边缘时加载相邻区间。 */
  const handleRequestMore = useCallback(
    (direction: KLineChartDirection) => {
      if (exhaustedRef.current[direction]) {
        return;
      }
      pendingRef.current[direction] = true;
      void runLoader();
    },
    [runLoader],
  );

  const handleRetry = useCallback(() => {
    setError(null);
    pendingInitialRef.current = true;
    pendingRef.current.before = true;
    void runLoader();
  }, [runLoader]);

  const quote = useMemo(() => {
    if (payload.candles.length === 0) {
      return null;
    }
    return buildStockQuoteSummary({
      symbol,
      name: stockName ?? undefined,
      period: KLINE_PERIOD,
      adjust: KLINE_ADJUST,
      candles: payload.candles,
      indicators: payload.indicators,
      meta: metaRef.current,
    });
  }, [payload, stockName, symbol]);

  const handleAskAI = useCallback(() => {
    navigate("/qa");
  }, [navigate]);

  const handleToggleWatch = useCallback(() => {
    // 预留：后续接入自选股接口后再做持久化。
    setWatched((value) => !value);
  }, []);

  const hasData = payload.candles.length > 0;
  const overlayStyle = {
    position: "absolute",
    inset: 0,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "rgba(9, 19, 27, 0.72)",
  } as const;

  if (error && !hasData) {
    return (
      <div className="stock-page">
        <ErrorState message={error} onRetry={handleRetry} />
      </div>
    );
  }

  return (
    <div className="stock-page">
      {error && hasData && (
        <div className="stale-banner" role="alert">
          刷新失败：{error}，当前展示上次加载的数据。
        </div>
      )}

      {quote && (
        <StockHeader
          quote={quote}
          watched={watched}
          onToggleWatch={handleToggleWatch}
          onAskAI={handleAskAI}
        />
      )}

      <div className="stock-layout">
        <section className="panel stock-main">
          <div className="stock-tabs" role="tablist" aria-label="个股分析标签页">
            {STOCK_TABS.map((tab) => (
              <button
                key={tab.key}
                type="button"
                role="tab"
                aria-selected={activeTab === tab.key}
                className={`stock-tab ${activeTab === tab.key ? "active" : ""}`}
                onClick={() => setActiveTab(tab.key)}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="stock-tab-content">
            {activeTab === "trend" && (
              <>
                <div className="stock-chart-box" style={{ position: "relative" }}>
                  <KLineChart
                    key={symbol}
                    data={payload}
                    height={395}
                    loading={loading}
                    hasMoreBefore={hasMoreBefore}
                    hasMoreAfter={hasMoreAfter}
                    onInitialViewport={handleInitialViewport}
                    onRequestMore={handleRequestMore}
                  />

                  {!hasData && !firstLoadDone && (
                    <div style={overlayStyle}>
                      <LoadingState text="行情数据加载中..." />
                    </div>
                  )}

                  {!hasData && firstLoadDone && (
                    <div style={overlayStyle}>
                      <EmptyState text="暂无该股票的行情数据" />
                    </div>
                  )}
                </div>

                <div className="ai-box">
                  <div className="ai-head">
                    ✦ AI 技术面解读
                    <span className="ai-sub">基于行情工具 + 技术指标知识库</span>
                  </div>
                  <Empty
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                    description="AI 技术面解读暂未接入"
                  />
                </div>
              </>
            )}

            {activeTab === "finance" && (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="财报数据暂未接入"
              />
            )}

            {activeTab === "score" && (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="综合评价数据暂未接入"
              />
            )}
          </div>
        </section>

        {quote && <StockSummaryAside quote={quote} onAskAI={handleAskAI} />}
      </div>
    </div>
  );
}

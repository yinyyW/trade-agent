import { useEffect, useMemo, useRef, useState } from "react";
import {
  CandlestickData,
  CandlestickSeries,
  HistogramData,
  HistogramSeries,
  IChartApi,
  ISeriesApi,
  LineData,
  LineSeries,
  LogicalRange,
  MouseEventParams,
  createChart,
} from "lightweight-charts";
import type { Candle, IndicatorResponse, IndicatorSeries } from "@/types/stock";

const MA_COLORS: Record<string, string> = {
  MA5: "#ff9800",
  MA10: "#36cfc9",
  MA20: "#4da3ff",
  MA60: "#9c27b0",
  MA250: "#0288d1",
};

const DEFAULT_MA_COLOR = "#666666";
const MIN_VISIBLE_BARS = 60;
const MAX_VISIBLE_BARS = 240;
const TARGET_BAR_SPACING = 8;
const PREFETCH_RATIO = 0.25;
const MIN_PREFETCH_BARS = 12;

/** K 线组件入参：已按时间排序并合并前端缓存后的数据。 */
export interface KLineChartPayload {
  candles: Candle[];
  indicators: IndicatorResponse[];
}

/** 数据加载方向：更早 / 更晚。 */
export type KLineChartDirection = "before" | "after";

interface KLineChartProps {
  data: KLineChartPayload;
  /** 图表高度，默认 395px。 */
  height?: number;
  /** 是否正在加载更多数据。 */
  loading?: boolean;
  /** 是否还可能有更早的数据。 */
  hasMoreBefore?: boolean;
  /** 是否还可能有更晚的数据。 */
  hasMoreAfter?: boolean;
  /** 首次确定可视窗口后回调，参数为一屏可容纳的 K 线数量。 */
  onInitialViewport?: (visibleBars: number) => void;
  /** 拖动到数据边缘时请求加载更多数据。 */
  onRequestMore?: (direction: KLineChartDirection) => void;
}

interface MaLegendItem {
  name: string;
  color: string;
}

/**
 * 个股 K 线图组件。
 *
 * 图表实例只在挂载时创建一次，后续数据变化仅通过 setData 更新，
 * 这样可以在前后追加数据时保持用户当前的可视区间稳定。
 *
 * 组件自身不请求接口，只负责：
 * 1. 上报首次视口可容纳的 K 线数量（用于确定初始时间范围）；
 * 2. 在用户拖动到数据边缘时通知父组件加载更多数据；
 * 3. 在左上角展示随十字光标变化的 MA 图例。
 */
export default function KLineChart({
  data,
  height = 395,
  loading = false,
  hasMoreBefore = false,
  hasMoreAfter = false,
  onInitialViewport,
  onRequestMore,
}: KLineChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const maLineSeriesRef = useRef<Map<string, ISeriesApi<"Line">>>(new Map());
  const maSeriesDataRef = useRef<IndicatorSeries[]>([]);
  const timeIndexRef = useRef<Map<string, number>>(new Map());
  const candleCountRef = useRef(0);
  const initialVisibleBarsRef = useRef(MIN_VISIBLE_BARS);
  const viewportReportedRef = useRef(false);
  const viewInitializedRef = useRef(false);
  const lastHoverIndexRef = useRef<number | undefined>(undefined);
  const onInitialViewportRef = useRef(onInitialViewport);
  const onRequestMoreRef = useRef(onRequestMore);
  const hasMoreBeforeRef = useRef(hasMoreBefore);
  const hasMoreAfterRef = useRef(hasMoreAfter);
  const [hoverValues, setHoverValues] = useState<Record<
    string,
    number | null
  > | null>(null);

  onInitialViewportRef.current = onInitialViewport;
  onRequestMoreRef.current = onRequestMore;
  hasMoreBeforeRef.current = hasMoreBefore;
  hasMoreAfterRef.current = hasMoreAfter;

  const maSeriesList = useMemo(() => {
    const indicator = data.indicators.find((item) => item.name === "MA");
    return indicator?.series ?? [];
  }, [data]);

  const maItems = useMemo<MaLegendItem[]>(
    () =>
      maSeriesList.map((series) => ({
        name: series.name,
        color: MA_COLORS[series.name] || DEFAULT_MA_COLOR,
      })),
    [maSeriesList],
  );

  const lastValues = useMemo<Record<string, number | null>>(() => {
    const values: Record<string, number | null> = {};
    maSeriesList.forEach((series) => {
      const last = series.values[series.values.length - 1];
      values[series.name] = last === undefined ? null : last;
    });
    return values;
  }, [maSeriesList]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return;
    }

    const chart = createChart(container, {
      width: container.clientWidth,
      height,
      layout: {
        background: { color: "#0a151e" },
        textColor: "#8da0af",
      },
      grid: {
        vertLines: { color: "rgba(74, 110, 128, 0.11)" },
        horzLines: { color: "rgba(74, 110, 128, 0.11)" },
      },
    });
    chartRef.current = chart;

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#ef5350",
      downColor: "#26a69a",
      borderUpColor: "#ef5350",
      borderDownColor: "#26a69a",
      wickUpColor: "#ef5350",
      wickDownColor: "#26a69a",
      lastValueVisible: false,
    });
    candleSeriesRef.current = candleSeries;

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "",
      lastValueVisible: false,
      priceLineVisible: false,
    });
    volumeSeriesRef.current = volumeSeries;
    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.82,
        bottom: 0,
      },
    });

    // 首屏宽度可能为 0（容器尚未完成布局），此时交给 ResizeObserver 补报，
    // 避免父组件一直等不到初始可视区间而不加载数据。
    const reportInitialViewport = (width: number) => {
      if (viewportReportedRef.current || width <= 0) {
        return;
      }
      viewportReportedRef.current = true;
      const visibleBars = Math.min(
        MAX_VISIBLE_BARS,
        Math.max(MIN_VISIBLE_BARS, Math.round(width / TARGET_BAR_SPACING)),
      );
      initialVisibleBarsRef.current = visibleBars;
      onInitialViewportRef.current?.(visibleBars);
    };

    reportInitialViewport(container.clientWidth);

    const handleCrosshairMove = (param: MouseEventParams) => {
      if (param.time === undefined || param.point === undefined) {
        if (lastHoverIndexRef.current !== undefined) {
          lastHoverIndexRef.current = undefined;
          setHoverValues(null);
        }
        return;
      }

      const seriesList = maSeriesDataRef.current;
      if (seriesList.length === 0) {
        return;
      }

      const index =
        param.logical !== undefined
          ? Number(param.logical)
          : timeIndexRef.current.get(String(param.time));
      if (
        index === undefined ||
        index < 0 ||
        index === lastHoverIndexRef.current
      ) {
        return;
      }
      lastHoverIndexRef.current = index;

      const next: Record<string, number | null> = {};
      seriesList.forEach((series) => {
        const value = series.values[index];
        next[series.name] = value === undefined ? null : value;
      });
      setHoverValues(next);
    };

    const handleVisibleRangeChange = (range: LogicalRange | null) => {
      const total = candleCountRef.current;
      if (!range || total <= 0) {
        return;
      }

      const prefetchBars = Math.max(
        MIN_PREFETCH_BARS,
        Math.round(initialVisibleBarsRef.current * PREFETCH_RATIO),
      );

      if (range.from <= prefetchBars && hasMoreBeforeRef.current) {
        onRequestMoreRef.current?.("before");
      }

      if (range.to >= total - 1 - prefetchBars && hasMoreAfterRef.current) {
        onRequestMoreRef.current?.("after");
      }
    };

    chart.subscribeCrosshairMove(handleCrosshairMove);
    chart
      .timeScale()
      .subscribeVisibleLogicalRangeChange(handleVisibleRangeChange);

    const resizeObserver = new ResizeObserver(() => {
      const width = container.clientWidth;
      if (width > 0) {
        chart.applyOptions({ width });
        reportInitialViewport(width);
      }
    });
    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      chart.unsubscribeCrosshairMove(handleCrosshairMove);
      chart
        .timeScale()
        .unsubscribeVisibleLogicalRangeChange(handleVisibleRangeChange);
      maLineSeriesRef.current = new Map();
      candleSeriesRef.current = null;
      volumeSeriesRef.current = null;
      chartRef.current = null;
      chart.remove();
    };
  }, [height]);

  useEffect(() => {
    const chart = chartRef.current;
    const candleSeries = candleSeriesRef.current;
    const volumeSeries = volumeSeriesRef.current;
    if (!chart || !candleSeries || !volumeSeries) {
      return;
    }

    const { candles, indicators } = data;
    const candleData: CandlestickData[] = [];
    const volumeData: HistogramData[] = [];
    const timeIndex = new Map<string, number>();

    candles.forEach((item, index) => {
      const open = Number(item.open);
      const close = Number(item.close);
      timeIndex.set(String(item.time), index);

      candleData.push({
        time: item.time,
        open,
        high: Number(item.high),
        low: Number(item.low),
        close,
      });

      volumeData.push({
        time: item.time,
        value: Number(item.volume),
        color: close >= open ? "#ef5350" : "#26a69a",
      });
    });

    candleSeries.setData(candleData);
    volumeSeries.setData(volumeData);
    timeIndexRef.current = timeIndex;

    const maIndicator = indicators.find((item) => item.name === "MA");
    const maSeries = maIndicator?.series ?? [];
    const activeNames = new Set<string>();
    const candleScaleId = candleSeries.options().priceScaleId;

    maSeries.forEach((series) => {
      activeNames.add(series.name);

      let lineSeries = maLineSeriesRef.current.get(series.name);
      if (!lineSeries) {
        lineSeries = chart.addSeries(LineSeries, {
          priceScaleId: candleScaleId,
          lineWidth: 2,
          color: MA_COLORS[series.name] || DEFAULT_MA_COLOR,
          lastValueVisible: false,
          priceLineVisible: false,
        });
        maLineSeriesRef.current.set(series.name, lineSeries);
      }

      const lineData: LineData[] = [];
      for (let index = 0; index < series.values.length; index++) {
        const value = series.values[index];
        const time = candles[index]?.time;
        if (value !== null && value !== undefined && time !== undefined) {
          lineData.push({ time, value: Number(value) });
        }
      }
      lineSeries.setData(lineData);
    });

    maLineSeriesRef.current.forEach((lineSeries, name) => {
      if (!activeNames.has(name)) {
        chart.removeSeries(lineSeries);
        maLineSeriesRef.current.delete(name);
      }
    });

    maSeriesDataRef.current = maSeries;
    candleCountRef.current = candles.length;
    lastHoverIndexRef.current = undefined;
    setHoverValues(null);

    if (candles.length === 0) {
      return;
    }

    // 可视区间无需在这里手动平移：lightweight-charts 的时间轴以「最后一根 K 线」
    // 为锚点（rightOffset + baseIndex），向前补数据时库自身会让同一批 K 线保持在
    // 原来的位置。若再按新增根数平移一次，画面会向新数据方向跳动。
    if (!viewInitializedRef.current) {
      const visibleBars = Math.min(
        initialVisibleBarsRef.current,
        candles.length,
      );
      chart.timeScale().setVisibleLogicalRange({
        from: candles.length - visibleBars,
        to: candles.length - 1,
      });
      viewInitializedRef.current = true;
    }
  }, [data]);

  const displayedValues = hoverValues ?? lastValues;

  return (
    <div className="kline-chart">
      <div
        ref={containerRef}
        className="kline-chart-canvas"
        style={{ height: `${height}px` }}
      />
      {loading && (
        <div
          style={{
            position: "absolute",
            top: 10,
            right: 14,
            zIndex: 2,
            fontSize: 12,
            color: "#91ebe5",
            pointerEvents: "none",
          }}
        >
          加载中…
        </div>
      )}
      {maItems.length > 0 && (
        <div className="kline-chart-legend">
          <span className="kline-legend-period">日线</span>
          {maItems.map((item) => {
            const value = displayedValues[item.name];
            return (
              <span className="kline-legend-item" key={item.name}>
                <span
                  className="kline-legend-swatch"
                  style={{ backgroundColor: item.color }}
                />
                <span className="kline-legend-name">{item.name}</span>
                <span
                  className="kline-legend-value"
                  style={{ color: item.color }}
                >
                  {value === null || value === undefined
                    ? "--"
                    : Number(value).toFixed(2)}
                </span>
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}

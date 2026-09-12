import { useEffect, useMemo, useRef, useState } from "react";
import {
  CandlestickData,
  CandlestickSeries,
  HistogramData,
  HistogramSeries,
  LineData,
  LineSeries,
  MouseEventParams,
  createChart,
} from "lightweight-charts";
import type { MarketKlineResponse } from "@/types/stock";

const MA_COLORS: Record<string, string> = {
  MA5: "#ff9800",
  MA10: "#36cfc9",
  MA20: "#4da3ff",
  MA60: "#9c27b0",
  MA250: "#0288d1",
};

const DEFAULT_MA_COLOR = "#666666";

interface KLineChartProps {
  data: MarketKlineResponse;
  /** 图表高度，默认 395px。 */
  height?: number;
}

interface MaLegendItem {
  name: string;
  color: string;
}

/**
 * 个股 K 线图组件。
 *
 * 基于 lightweight-charts 绘制蜡烛图、成交量与 MA 叠加线，
 * 数据直接使用 /api/v1/market/kline 的响应结构。
 *
 * MA 指标的数值与颜色统一展示在图表左上角，并跟随十字光标
 * 展示对应交易日的均线值；价格轴上的固定数值标签已关闭。
 */
export default function KLineChart({ data, height = 395 }: KLineChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const lastHoverIndexRef = useRef<number | undefined>(undefined);
  const [hoverValues, setHoverValues] = useState<Record<
    string,
    number | null
  > | null>(null);

  const maSeries = useMemo(() => {
    const indicator = data.indicators.find((item) => item.name === "MA");
    return indicator?.series ?? [];
  }, [data]);

  const maItems = useMemo<MaLegendItem[]>(
    () =>
      maSeries.map((series) => ({
        name: series.name,
        color: MA_COLORS[series.name] || DEFAULT_MA_COLOR,
      })),
    [maSeries],
  );

  const lastValues = useMemo<Record<string, number | null>>(() => {
    const values: Record<string, number | null> = {};
    maSeries.forEach((series) => {
      const last = series.values[series.values.length - 1];
      values[series.name] = last === undefined ? null : last;
    });
    return values;
  }, [maSeries]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) {
      return;
    }

    lastHoverIndexRef.current = undefined;
    setHoverValues(null);

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
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#ef5350",
      downColor: "#26a69a",
      borderUpColor: "#ef5350",
      borderDownColor: "#26a69a",
      wickUpColor: "#ef5350",
      wickDownColor: "#26a69a",
      // 关闭价格轴上的固定数值标签，统一改用左上角图例。
      lastValueVisible: false,
    });

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "",
      lastValueVisible: false,
      priceLineVisible: false,
    });
    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.82,
        bottom: 0,
      },
    });

    const candleData: CandlestickData[] = [];
    const volumeData: HistogramData[] = [];
    const timeIndexMap = new Map<string, number>();

    data.candles.forEach((item, index) => {
      const open = Number(item.open);
      const close = Number(item.close);
      timeIndexMap.set(String(item.time), index);

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

    const candleScaleId = candleSeries.options().priceScaleId;
    maSeries.forEach((series) => {
      const lineData: LineData[] = [];

      for (let index = 0; index < series.values.length; index++) {
        const value = series.values[index];
        const time = data.candles[index]?.time;
        if (value !== null && value !== undefined && time !== undefined) {
          lineData.push({
            time,
            value: Number(value),
          });
        }
      }

      const lineSeries = chart.addSeries(LineSeries, {
        priceScaleId: candleScaleId,
        lineWidth: 2,
        color: MA_COLORS[series.name] || DEFAULT_MA_COLOR,
        lastValueVisible: false,
        priceLineVisible: false,
      });
      lineSeries.setData(lineData);
    });

    chart.timeScale().fitContent();

    const handleCrosshairMove = (param: MouseEventParams) => {
      if (param.time === undefined || param.point === undefined) {
        if (lastHoverIndexRef.current !== undefined) {
          lastHoverIndexRef.current = undefined;
          setHoverValues(null);
        }
        return;
      }

      const index =
        param.logical !== undefined
          ? Number(param.logical)
          : timeIndexMap.get(String(param.time));
      if (
        index === undefined ||
        index < 0 ||
        index === lastHoverIndexRef.current
      ) {
        return;
      }
      lastHoverIndexRef.current = index;

      const next: Record<string, number | null> = {};
      maSeries.forEach((series) => {
        const value = series.values[index];
        next[series.name] = value === undefined ? null : value;
      });
      setHoverValues(next);
    };
    chart.subscribeCrosshairMove(handleCrosshairMove);

    const resizeFn = () => {
      chart.applyOptions({ width: container.clientWidth });
    };
    window.addEventListener("resize", resizeFn);

    return () => {
      chart.unsubscribeCrosshairMove(handleCrosshairMove);
      window.removeEventListener("resize", resizeFn);
      chart.remove();
    };
  }, [data, height, maSeries]);

  const displayedValues = hoverValues ?? lastValues;

  return (
    <div className="kline-chart">
      <div
        ref={containerRef}
        className="kline-chart-canvas"
        style={{ height: `${height}px` }}
      />
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
                    : `${Number(value).toFixed(2)}`}
                </span>
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}

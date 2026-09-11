import { useEffect, useRef, useState } from "react";
import {
  createChart,
  IChartApi,
  ISeriesApi,
  CandlestickSeries,
  HistogramSeries,
  LineSeries,
  CandlestickData,
  HistogramData,
  LineData,
} from "lightweight-charts";
import { MarketKlineRequest, MarketKlineResponse } from "@/types/stock";
import { fetchMarketKline } from "@/api/stock";

function KLineChart({ data }: { data: MarketKlineResponse }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  // 保存均线系列引用，方便销毁重绘
  const overlayLinesRef = useRef<ISeriesApi<"Line">[]>([]);

  useEffect(() => {
    console.log("k线图组件数据: ", data);

    const container = containerRef.current;
    if (!container) return;

    const chart = createChart(container, {
      width: container.clientWidth,
      height: 620,
      layout: { background: { color: "#ffffff" }, textColor: "#333333" },
      grid: {
        vertLines: { color: "#eeeeee" },
        horzLines: { color: "#eeeeee" },
      },
    });
    chartRef.current = chart;

    // K线蜡烛图
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#ef5350",
      downColor: "#26a69a",
      borderUpColor: "#ef5350",
      borderDownColor: "#26a69a",
      wickUpColor: "#ef5350",
      wickDownColor: "#26a69a",
    });
    candleSeriesRef.current = candleSeries;

    // 成交量副图：移除 priceScale 配置！只保留基础series选项
    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "",
    });
    volumeSeriesRef.current = volumeSeries;

    // ========= 重点修复：单独给volume的priceScale设置scaleMargins =========
    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.82,
        bottom: 0,
      },
    });

    // ---- 数据转换（和之前一致） ----
    const candleData: CandlestickData[] = [];
    const volumeData: HistogramData[] = [];
    const timeList = data.candles.map((c) => c.time);

    data.candles.forEach((item) => {
      const open = Number(item.open);
      const close = Number(item.close);
      candleData.push({
        time: item.time,
        open,
        high: Number(item.high),
        low: Number(item.low),
        close,
      });
      const volColor = close >= open ? "#ef5350" : "#26a69a";
      volumeData.push({
        time: item.time,
        value: Number(item.volume),
        color: volColor,
      });
    });

    candleSeries.setData(candleData);
    volumeSeries.setData(volumeData);

    // ---- MA 叠加线（v5：addSeries + LineSeries） ----
    const maIndicator = data.indicators.find((ind) => ind.name === "MA");
    if (maIndicator) {
      maIndicator.series.forEach((ser) => {
        const lineData: LineData[] = [];
        for (let i = 0; i < ser.values.length; i++) {
          const val = ser.values[i];
          if (val !== null) {
            lineData.push({ time: timeList[i], value: Number(val) });
          }
        }
        const colorMap: Record<string, string> = {
          MA5: "#ff9800",
          MA60: "#9c27b0",
          MA250: "#0288d1",
        };
        const candleScaleId = candleSeries.options().priceScaleId; // "right"
        const lineSeries = chart.addSeries(LineSeries, {
          priceScaleId: candleScaleId, // 和蜡烛图同一坐标轴
          lineWidth: 2,
          color: colorMap[ser.name] || "#666666",
          title: ser.name,
        });
        lineSeries.setData(lineData);
        overlayLinesRef.current.push(lineSeries);
      });
    }

    chart.timeScale().fitContent();

    const resizeFn = () => chart.applyOptions({ width: container.clientWidth });
    window.addEventListener("resize", resizeFn);

    return () => {
      window.removeEventListener("resize", resizeFn);
      overlayLinesRef.current = [];
      chart.remove();
    };
  }, [data]);

  return <div ref={containerRef} style={{ width: "100%", height: "620px" }} />;
}

export default function StockPage() {
  const [klineRes, setKlineRes] = useState<MarketKlineResponse | null>(null);

  useEffect(() => {
    const param: MarketKlineRequest = {
      symbol: "sh600519",
      period: "1d",
      adjust: "qfq",
      start: "2026-01-01",
      end: "2026-09-10",
      indicators: [
        {
          name: "MA",
          params: {
            periods: [5, 60, 250],
          },
        },

        {
          name: "EMA",
          params: {
            periods: [5, 60, 250],
          },
        },
      ],
    };
    console.log("获取个股数据");
    fetchMarketKline(param)
      .then((res) => {
        console.log("获取个股数据，", res);
        if (res) {
          setKlineRes(res);
        }
      })
      .catch((e) => {
        console.log("获取k线数据失败");
      });
  }, []);

  return <div>{klineRes && <KLineChart data={klineRes} />}</div>;
}

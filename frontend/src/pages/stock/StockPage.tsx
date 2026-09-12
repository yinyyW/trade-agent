import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Empty } from "antd";
import { fetchMarketKline } from "@/api/stock";
import { getErrorMessage } from "@/api/http";
import { EmptyState, ErrorState, LoadingState } from "@/components/common/Status";
import KLineChart from "@/components/market/KLineChart";
import StockHeader from "@/components/market/StockHeader";
import StockSummaryAside from "@/components/market/StockSummaryAside";
import type { MarketKlineResponse } from "@/types/stock";
import {
  buildStockQuoteSummary,
  normalizeStockSymbol,
} from "@/utils/stock";
import "@/styles/stock.css";

type StockTabKey = "trend" | "finance" | "score";

const STOCK_TABS: Array<{ key: StockTabKey; label: string }> = [
  { key: "trend", label: "走势分析" },
  { key: "finance", label: "财报解读" },
  { key: "score", label: "综合评价" },
];

function formatDateForApi(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

/**
 * 个股分析详情页。
 *
 * 股票代码通过 /stock/:symbol 路由参数进入，页面头部行情与 K 线图
 * 复用 /api/v1/market/kline 数据；财报与综合评价依赖的 AI 接口暂未
 * 接入，因此只保留对应 Tab 的空状态。
 */
export default function StockPage() {
  const { symbol: routeSymbol } = useParams<{ symbol: string }>();
  const navigate = useNavigate();
  const [kline, setKline] = useState<MarketKlineResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<StockTabKey>("trend");
  const [watched, setWatched] = useState(false);

  const symbol = normalizeStockSymbol(routeSymbol);

  const loadKline = useCallback(async () => {
    const now = new Date();
    const start = new Date(
      now.getFullYear() - 1,
      now.getMonth(),
      now.getDate(),
    );

    setLoading(true);
    setError(null);

    try {
      const response = await fetchMarketKline({
        symbol,
        period: "1d",
        adjust: "qfq",
        start: formatDateForApi(start),
        end: formatDateForApi(now),
        indicators: [
          {
            name: "MA",
            params: { periods: [5, 10, 20] },
          },
        ],
      });
      setKline(response);
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    void loadKline();
  }, [loadKline]);

  const quote = useMemo(
    () => (kline ? buildStockQuoteSummary(kline) : null),
    [kline],
  );

  const handleAskAI = useCallback(() => {
    navigate("/qa");
  }, [navigate]);

  const handleToggleWatch = useCallback(() => {
    // 预留：后续接入自选股接口后再做持久化。
    setWatched((value) => !value);
  }, []);

  if (loading && !kline) {
    return (
      <div className="stock-page">
        <LoadingState text="行情数据加载中..." />
      </div>
    );
  }

  if (error && !kline) {
    return (
      <div className="stock-page">
        <ErrorState message={error} onRetry={loadKline} />
      </div>
    );
  }

  if (kline && kline.candles.length === 0) {
    return (
      <div className="stock-page">
        <EmptyState text="暂无该股票的行情数据" />
      </div>
    );
  }

  return (
    <div className="stock-page">
      {error && (
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
                <div className="stock-chart-box">
                  {kline && <KLineChart data={kline} height={395} />}
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

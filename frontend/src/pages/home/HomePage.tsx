import { useHomeDashboard } from "../../hooks/useHomeDashboard";
import ComplianceFooter from "../../components/common/ComplianceFooter";
import { ErrorState } from "../../components/common/Status";
import HomeSkeleton from "../../components/home/HomeSkeleton";
import HotSectorPanel from "../../components/home/HotSectorPanel";
import MarketOverviewCard from "../../components/home/MarketOverviewCard";
import NewsPanel from "../../components/home/NewsPanel";
import PageHead from "../../components/home/PageHead";
import TopBar from "../../components/home/TopBar";
import "@/styles/home.css";

/**
 * 首页：市场热点复盘页。
 *
 * 数据来自 GET /api/home/dashboard，页面包含：
 * 1. 市场速览：上证指数 / 深证成指 / 创业板指；
 * 2. 热点资讯：当日热点 / 近 3 日热点 Tab 切换；
 * 3. 热门行业 TOP10（当前仅展示行业名称）。
 * 宏观环境模块按需求暂不展示。
 */
export default function HomePage() {
  const { data, loading, error, reload } = useHomeDashboard();

  return (
    <div className="app">
      <TopBar />
      <main className="wrap">
        {loading && !data ? (
          <HomeSkeleton />
        ) : error && !data ? (
          <>
            <PageHead />
            <ErrorState message={error} onRetry={reload} />
          </>
        ) : data ? (
          <>
            <PageHead
              updateTime={data.update_time}
              onRefresh={reload}
              refreshing={loading}
            />
            {error && (
              <div className="stale-banner" role="alert">
                刷新失败：{error}，当前展示上次加载的数据。
              </div>
            )}
            <MarketOverviewCard indices={data.market?.indices ?? []} />
            <div className="grid-main">
              <NewsPanel news={data.news ?? []} />
              <HotSectorPanel sectors={data.sectors ?? []} />
            </div>
          </>
        ) : null}
      </main>
      <ComplianceFooter />
    </div>
  );
}

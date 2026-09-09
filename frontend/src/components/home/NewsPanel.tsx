import { useMemo, useState } from "react";
import {
  NEWS_TAB_TODAY,
  NEWS_TAB_THREE_DAYS,
  type NewsTabKey,
} from "../../constants/home";
import type { HotNewsVO } from "../../types/home";
import { filterNewsForTab } from "../../utils/news";
import { EmptyState } from "../common/Status";
import NewsItem from "./NewsItem";

const TABS: Array<{ key: NewsTabKey; label: string }> = [
  { key: NEWS_TAB_TODAY, label: "当日热点" },
  { key: NEWS_TAB_THREE_DAYS, label: "近3日热点" },
];

interface NewsPanelProps {
  news: HotNewsVO[];
}

/** 热点资讯列表，支持当日 / 近 3 日 Tab 切换。 */
export default function NewsPanel({ news }: NewsPanelProps) {
  const [activeTab, setActiveTab] = useState<NewsTabKey>(NEWS_TAB_TODAY);
  const visibleNews = useMemo(
    () => filterNewsForTab(news, activeTab),
    [news, activeTab],
  );
  const emptyText =
    activeTab === NEWS_TAB_TODAY ? "暂无当日热点资讯" : "暂无近3日热点资讯";

  return (
    <section className="panel">
      <div className="panel-hd">
        <div className="panel-title">热点资讯</div>
        <div className="tabs" role="tablist" aria-label="热点资讯时间范围">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              type="button"
              role="tab"
              aria-selected={activeTab === tab.key}
              className={`tab ${activeTab === tab.key ? "active" : ""}`}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      {visibleNews.length === 0 ? (
        <EmptyState text={emptyText} />
      ) : (
        <div className="news-list">
          {visibleNews.map((item, index) => (
            <NewsItem
              key={`${item.publish_time ?? "news"}-${item.title}-${index}`}
              news={item}
            />
          ))}
        </div>
      )}
    </section>
  );
}

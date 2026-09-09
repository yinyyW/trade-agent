import type { IndexQuoteVO } from "../../types/home";
import { EmptyState } from "../common/Status";
import IndexQuoteCard from "./IndexQuoteCard";

interface MarketOverviewCardProps {
  indices: IndexQuoteVO[];
}

/**
 * 市场速览卡片。
 *
 * 按需求调整：仅展示后端接口返回的上证指数、深证成指、创业板指。
 * 原 UX 中的成交额 / 北向资金 / 涨跌家数等指标暂未由当前接口提供，不再展示。
 */
export default function MarketOverviewCard({
  indices,
}: MarketOverviewCardProps) {
  return (
    <section className="ai-card">
      <div className="ai-top">
        <span className="ai-dot" aria-hidden="true" />
        市场速览
      </div>
      {indices.length === 0 ? (
        <EmptyState text="暂无指数行情数据" />
      ) : (
        <div className="index-quotes">
          {indices.map((quote) => (
            <IndexQuoteCard key={quote.code || quote.name} quote={quote} />
          ))}
        </div>
      )}
    </section>
  );
}

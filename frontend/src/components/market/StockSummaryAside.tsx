import { Button, Empty } from "antd";
import type { StockQuoteSummary } from "@/types/stock";

interface StockSummaryAsideProps {
  quote: StockQuoteSummary;
  onAskAI: () => void;
}

/**
 * 个股详情页右侧 AI 当前标的摘要。
 *
 * 基本面 / 技术面 / 板块热度与风险扫描依赖后端 AI 分析接口，
 * 当前接口尚未接入，因此仅保留摘要卡片结构与跳转入口。
 */
export default function StockSummaryAside({
  quote,
  onAskAI,
}: StockSummaryAsideProps) {
  return (
    <aside className="panel stock-aside">
      <div className="stock-aside-head">
        <div className="stock-aside-title">✦ AI 当前标的摘要</div>
        <span className="stock-aside-lock">MCP 已锁定</span>
      </div>

      <div className="stock-aside-symbol">
        {quote.name ?? "--"} · {quote.code}
      </div>

      <div className="stock-aside-score">
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="AI 摘要数据暂未接入"
        />
      </div>

      <Button type="primary" block onClick={onAskAI}>
        继续向 AI 提问 →
      </Button>

      <div className="stock-aside-source">
        <span>数据来源</span>
        行情 / 财报 / 资讯聚合 / RAG 知识库
      </div>
    </aside>
  );
}

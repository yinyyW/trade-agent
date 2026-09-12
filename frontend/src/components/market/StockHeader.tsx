import { Button, Space } from "antd";
import type { StockQuoteSummary } from "@/types/stock";
import {
  formatPrice,
  formatSignedNumber,
  formatSignedPercent,
} from "@/utils/format";
import { getStockTrendClass } from "@/utils/stock";

interface StockHeaderProps {
  quote: StockQuoteSummary;
  watched: boolean;
  onToggleWatch: () => void;
  onAskAI: () => void;
}

/** 个股详情页顶部行情头部。 */
export default function StockHeader({
  quote,
  watched,
  onToggleWatch,
  onAskAI,
}: StockHeaderProps) {
  const trendClass = getStockTrendClass(quote.change);
  const turnover =
    quote.turnover === null ? "--" : `${formatPrice(quote.turnover, 2)}%`;

  return (
    <section className="stock-ticker">
      <div className="stock-ticker-top">
        <div>
          <Space align="baseline" size={8}>
            <span className="stock-name">{quote.name ?? "--"}</span>
            <span className="stock-code">{quote.code}</span>
          </Space>
          <Space align="baseline" size={16} className="stock-price-row">
            <span className={`stock-price ${trendClass}`}>
              {formatPrice(quote.price)}
            </span>
            <span className={`stock-change ${trendClass}`}>
              {formatSignedNumber(quote.change)}{" "}
              {formatSignedPercent(quote.changePercent)}
            </span>
          </Space>
        </div>
        <Space size={8} className="stock-actions">
          <Button onClick={onToggleWatch}>
            {watched ? "★ 已自选" : "☆ 加自选"}
          </Button>
          <Button type="primary" onClick={onAskAI}>
            ✦ 问 AI
          </Button>
        </Space>
      </div>

      <div className="stock-stats">
        <div className="stock-stat">
          <span>今开</span>
          <b>{formatPrice(quote.open)}</b>
        </div>
        <div className="stock-stat">
          <span>最高</span>
          <b>{formatPrice(quote.high)}</b>
        </div>
        <div className="stock-stat">
          <span>最低</span>
          <b>{formatPrice(quote.low)}</b>
        </div>
        <div className="stock-stat">
          <span>换手率</span>
          <b>{turnover}</b>
        </div>
      </div>
    </section>
  );
}

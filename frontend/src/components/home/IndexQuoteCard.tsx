import { INDEX_FALLBACK_NAMES } from "../../constants/home";
import type { IndexQuoteVO } from "../../types/home";
import {
  formatPrice,
  formatSignedNumber,
  formatSignedPercent,
  toNumber,
} from "../../utils/format";

function getTrendClass(value: number | string): "up" | "down" | "flat" {
  const numericValue = toNumber(value);
  if (numericValue === null) {
    return "flat";
  }
  if (numericValue > 0) {
    return "up";
  }
  if (numericValue < 0) {
    return "down";
  }
  return "flat";
}

interface IndexQuoteCardProps {
  quote: IndexQuoteVO;
}

/** 单个指数行情卡片。A 股红涨绿跌。 */
export default function IndexQuoteCard({ quote }: IndexQuoteCardProps) {
  const displayName = quote.name || INDEX_FALLBACK_NAMES[quote.code] || "指数";
  const trendClass = getTrendClass(quote.change);

  return (
    <article className="index-quote">
      <div className="index-quote-name">{displayName}</div>
      <div className={`index-quote-price ${trendClass}`}>
        {formatPrice(quote.price)}
      </div>
      <div className="index-quote-change">
        <span className={trendClass}>{formatSignedNumber(quote.change)}</span>
        <span className={`index-quote-percent ${trendClass}`}>
          {formatSignedPercent(quote.change_percent)}
        </span>
      </div>
    </article>
  );
}

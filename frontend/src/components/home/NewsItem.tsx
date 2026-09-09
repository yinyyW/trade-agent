import type { HotNewsVO } from "../../types/home";
import { formatNewsTime } from "../../utils/format";

interface NewsItemProps {
  news: HotNewsVO;
}

/**
 * 单条热点新闻。
 *
 * 当前接口只提供 title / summary / source / publish_time / url，
 * 不提供利好利空标签与 AI 解读，因此不伪造情绪标签。
 * 悬浮时展示完整摘要与原文链接。
 */
export default function NewsItem({ news }: NewsItemProps) {
  const { title, summary, source, publish_time: publishTime, url } = news;

  return (
    <article className="news">
      <div className="news-row">
        <span className="time">{formatNewsTime(publishTime)}</span>
        <div className="news-main">
          <div className="news-title">{title}</div>
          {summary && <div className="news-desc">{summary}</div>}
        </div>
        {source && <span className="news-source">{source}</span>}
      </div>
      {(summary || url) && (
        <div className="news-extra">
          {summary && <div className="news-extra-summary">{summary}</div>}
          {url && (
            <a
              className="news-link"
              href={url}
              target="_blank"
              rel="noreferrer"
            >
              查看原文 ↗
            </a>
          )}
        </div>
      )}
    </article>
  );
}

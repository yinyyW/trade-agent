import { formatDateTime } from "../../utils/format";

interface PageHeadProps {
  updateTime?: string | null;
  onRefresh?: () => void;
  refreshing?: boolean;
}

/** 页面标题、更新时间与刷新操作区。 */
export default function PageHead({
  updateTime,
  onRefresh,
  refreshing = false,
}: PageHeadProps) {
  return (
    <div className="page-head">
      <div>
        <div className="eyebrow">MARKET INTELLIGENCE</div>
        <h1 className="page-title">市场复盘</h1>
        <div className="update">
          数据更新时间：{formatDateTime(updateTime)}
        </div>
      </div>
      {onRefresh && (
        <button
          type="button"
          className="refresh-btn"
          onClick={onRefresh}
          disabled={refreshing}
        >
          {refreshing ? "刷新中..." : "刷新数据"}
        </button>
      )}
    </div>
  );
}

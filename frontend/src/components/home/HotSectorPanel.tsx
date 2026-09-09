import type { HotSectorVO } from "../../types/home";
import { EmptyState } from "../common/Status";

const MAX_SECTORS = 10;

interface HotSectorPanelProps {
  sectors: HotSectorVO[];
}

/**
 * 热门行业 TOP10。
 *
 * 当前后端接口只稳定提供行业 code / name，因此仅展示行业名称，
 * 不展示原 UX 中的涨幅与成交活跃度。
 */
export default function HotSectorPanel({ sectors }: HotSectorPanelProps) {
  const visibleSectors = sectors.slice(0, MAX_SECTORS);

  return (
    <aside className="panel">
      <div className="panel-hd">
        <div className="panel-title">热门行业 TOP10</div>
        <span className="update">今日</span>
      </div>
      {visibleSectors.length === 0 ? (
        <EmptyState text="暂无热门行业数据" />
      ) : (
        <div className="rank-list">
          {visibleSectors.map((sector, index) => (
            <div
              className="rank"
              key={sector.code || `${sector.name}-${index}`}
            >
              <div className="rank-num">{String(index + 1).padStart(2, "0")}</div>
              <div className="rank-name">{sector.name}</div>
            </div>
          ))}
        </div>
      )}
    </aside>
  );
}

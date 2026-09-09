interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

/** 模块级加载状态。 */
export function LoadingState({ text = "数据加载中..." }: { text?: string }) {
  return (
    <div className="status-block" role="status">
      <span className="loading-spinner" aria-hidden="true" />
      <span className="status-desc">{text}</span>
    </div>
  );
}

/** 模块 / 页面级错误状态。 */
export function ErrorState({
  message = "数据加载失败，请稍后重试",
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="status-block" role="alert">
      <span className="status-icon" aria-hidden="true">⚠</span>
      <div className="status-title">数据加载失败</div>
      <div className="status-desc">{message}</div>
      {onRetry && (
        <button type="button" className="retry-btn" onClick={onRetry}>
          重新加载
        </button>
      )}
    </div>
  );
}

/** 模块级空状态。 */
export function EmptyState({ text = "暂无数据" }: { text?: string }) {
  return (
    <div className="status-block status-empty" role="status">
      <span className="status-icon" aria-hidden="true">◎</span>
      <span className="status-desc">{text}</span>
    </div>
  );
}

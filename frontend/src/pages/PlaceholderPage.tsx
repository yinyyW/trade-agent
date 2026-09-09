interface PlaceholderPageProps {
  title: string;
  description?: string;
}

/** 未完成页面的占位路由内容，保持全局 Header / Footer 不变。 */
export default function PlaceholderPage({
  title,
  description = "该页面正在建设中",
}: PlaceholderPageProps) {
  return (
    <section className="panel">
      <div className="panel-hd">
        <div className="panel-title">{title}</div>
      </div>
      <div className="status-block status-empty">
        <span className="status-icon" aria-hidden="true">◎</span>
        <span className="status-desc">{description}</span>
      </div>
    </section>
  );
}

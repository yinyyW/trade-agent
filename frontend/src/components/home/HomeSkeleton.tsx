import PageHead from "./PageHead";

/** 首页首次加载骨架屏。 */
export default function HomeSkeleton() {
  return (
    <>
      <PageHead />
      <section className="ai-card" aria-hidden="true">
        <div className="skeleton skeleton-heading" />
        <div className="index-quotes">
          <div className="skeleton skeleton-index" />
          <div className="skeleton skeleton-index" />
          <div className="skeleton skeleton-index" />
        </div>
      </section>
      <div className="grid-main">
        <section className="panel">
          <div className="panel-hd">
            <div className="skeleton skeleton-title" />
          </div>
          <div className="news-list">
            {Array.from({ length: 4 }).map((_, index) => (
              <div className="skeleton skeleton-news" key={index} />
            ))}
          </div>
        </section>
        <aside className="panel">
          <div className="panel-hd">
            <div className="skeleton skeleton-title" />
          </div>
          <div className="rank-list">
            {Array.from({ length: 6 }).map((_, index) => (
              <div className="skeleton skeleton-rank" key={index} />
            ))}
          </div>
        </aside>
      </div>
    </>
  );
}

import { useState } from "react";

interface NavItem {
  key: string;
  label: string;
  href: string;
  active?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { key: "market", label: "市场复盘", href: "#/market", active: true },
  { key: "stock", label: "个股分析", href: "#/stock" },
  { key: "qa", label: "AI问答", href: "#/qa" },
  { key: "watchlist", label: "自选股", href: "#/watchlist" },
];

/** 全局顶部导航栏。 */
export default function TopBar() {
  const [keyword, setKeyword] = useState("");

  const handleSearch = () => {
    // 预留：后续接入股票搜索接口后再发起请求。
  };

  return (
    <header className="topbar">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true" />
        <span>A股 AI</span>
      </div>
      <nav className="nav" aria-label="主导航">
        {NAV_ITEMS.map((item) => (
          <a
            key={item.key}
            className={item.active ? "active" : undefined}
            href={item.href}
          >
            {item.label}
          </a>
        ))}
      </nav>
      <div className="top-actions">
        <input
          className="search"
          type="search"
          placeholder="搜索股票 / 代码"
          value={keyword}
          onChange={(event) => setKeyword(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              handleSearch();
            }
          }}
          aria-label="搜索股票或代码"
        />
        <div className="avatar" aria-label="用户头像">AI</div>
      </div>
    </header>
  );
}

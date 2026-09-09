import { useCallback, useEffect, useState } from "react";
import { fetchHomeDashboard } from "../api/home";
import { getErrorMessage, isCancelError } from "../api/http";
import type { HomeDashboardVO } from "../types/home";

export interface HomeDashboardState {
  /** 最近一次成功加载的看板数据。 */
  data: HomeDashboardVO | null;
  /** 是否正在请求（首次加载或刷新）。 */
  loading: boolean;
  /** 最近一次失败信息。刷新失败时会保留旧数据。 */
  error: string | null;
  /** 手动触发重新加载。 */
  reload: () => void;
}

/**
 * 首页看板数据请求 Hook。
 *
 * 组件卸载或 effect 重跑时通过 AbortController 主动取消请求，避免内存泄漏。
 * 首次加载失败不保留数据；刷新失败时保留旧数据，由页面展示降级提示。
 */
export function useHomeDashboard(): HomeDashboardState {
  const [data, setData] = useState<HomeDashboardVO | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const reload = useCallback(() => {
    setReloadKey((key) => key + 1);
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;

    setLoading(true);
    setError(null);

    fetchHomeDashboard(controller.signal)
      .then((dashboard) => {
        if (!active) {
          return;
        }
        setData(dashboard);
      })
      .catch((requestError: unknown) => {
        if (!active || isCancelError(requestError)) {
          return;
        }
        setError(getErrorMessage(requestError));
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
      controller.abort();
    };
  }, [reloadKey]);

  return { data, loading, error, reload };
}

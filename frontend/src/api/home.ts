import type { ApiResponse, HomeDashboardVO } from "../types/home";
import { request } from "./http";

/**
 * 获取首页看板聚合数据。
 *
 * 对应后端接口：
 * GET /api/home/dashboard
 * backend/src/app/home/router.py
 */
export async function fetchHomeDashboard(
  signal?: AbortSignal,
): Promise<HomeDashboardVO> {
  const response = await request<ApiResponse<HomeDashboardVO>>({
    url: "/home/dashboard",
    method: "GET",
    signal,
  });

  return response.data;
}

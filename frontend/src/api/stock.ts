import { MarketKlineRequest, MarketKlineResponse } from "@/types/stock";
import { request } from "./http";
import { ApiResponse } from "@/types/home";

/**
 * 获取个股k线数据。
 *
 * 对应后端接口：
 * GET /api/v1/market/kline
 * backend/src/app/market/router.py
 */
export async function fetchMarketKline(
  marketKlineRequest: MarketKlineRequest,
): Promise<MarketKlineResponse> {
  // const response = await fetch("/api/v1/market/kline", {
  //   method: "POST",
  //   headers: {
  //     "Content-Type": "application/json",
  //   },
  //   body: JSON.stringify(request),
  // });

  // if (!response.ok) {
  //   throw new Error(`HTTP ${response.status}`);
  // }

  // return response.json();

  const response = await request<ApiResponse<MarketKlineResponse>>({
    url: "/api/v1/market/kline",
    method: "POST",
    data: marketKlineRequest,
  });

  return response.data;
}

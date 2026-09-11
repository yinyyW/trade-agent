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
  const response = await request<ApiResponse<MarketKlineResponse>>({
    url: "/v1/market/kline",
    method: "POST",
    data: marketKlineRequest,
  });
  return response.data;
}

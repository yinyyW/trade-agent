import axios, { AxiosError, type AxiosRequestConfig } from "axios";
import { DEFAULT_ERROR_MESSAGE } from "../constants/home";

/** 统一的业务 / 网络异常对象。 */
export class ApiError extends Error {
  readonly code: number;

  constructor(message: string, code = -1) {
    super(message);
    this.name = "ApiError";
    this.code = code;
  }
}

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
});

// 预留：统一注入登录态 / MCP 会话上下文等公共请求头。
http.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error),
);

http.interceptors.response.use(
  (response) => {
    const payload = response.data;

    if (
      payload &&
      typeof payload === "object" &&
      "code" in payload &&
      payload.code !== 0
    ) {
      return Promise.reject(
        new ApiError(payload.message || DEFAULT_ERROR_MESSAGE, payload.code),
      );
    }

    return payload;
  },
  (error: AxiosError) => Promise.reject(normalizeHttpError(error)),
);

/** 将 Axios 异常转换为对用户友好的 ApiError。 */
function normalizeHttpError(error: AxiosError): ApiError {
  if (axios.isCancel(error)) {
    return new ApiError("请求已取消", -3);
  }

  if (error.response) {
    const data = error.response.data as
      | { message?: string; detail?: string }
      | undefined;
    const message =
      data?.message || data?.detail || `服务异常（${error.response.status}）`;
    return new ApiError(message, error.response.status);
  }

  if (error.code === "ECONNABORTED") {
    return new ApiError("请求超时，请稍后重试", -2);
  }

  return new ApiError("网络连接失败，请检查网络后重试", -1);
}

/** 通用请求方法。响应拦截器已返回业务 payload，因此这里直接断言为 T。 */
export async function request<T>(config: AxiosRequestConfig): Promise<T> {
  return http.request(config) as unknown as Promise<T>;
}

/** 从任意异常中提取用户可读的错误信息。 */
export function getErrorMessage(
  error: unknown,
  fallback = DEFAULT_ERROR_MESSAGE,
): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return fallback;
}

/** 判断是否为组件卸载等场景触发的主动取消。 */
export function isCancelError(error: unknown): boolean {
  return axios.isCancel(error);
}

export default http;

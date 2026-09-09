/**
 * 首页模块常量与文案配置。
 */

/** 指数代码兜底名称，后端返回的 name 为空时使用。 */
export const INDEX_FALLBACK_NAMES: Record<string, string> = {
  s_sh000001: "上证指数",
  s_sz399001: "深证成指",
  s_sz399006: "创业板指",
};

/** 热点资讯 Tab 标识 */
export const NEWS_TAB_TODAY = "today";
export const NEWS_TAB_THREE_DAYS = "three_days";
export type NewsTabKey = typeof NEWS_TAB_TODAY | typeof NEWS_TAB_THREE_DAYS;

/** 默认异常提示 */
export const DEFAULT_ERROR_MESSAGE = "数据加载失败，请稍后重试";

/** 全站合规声明 */
export const COMPLIANCE_TEXT =
  "股市有风险，投资需谨慎。本工具仅提供数据客观解读，不构成任何投资建议。";

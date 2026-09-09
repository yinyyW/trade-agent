/**
 * 数值与时间格式化工具。
 */

const EMPTY_VALUE = "--";

/** 将后端返回的 number | string 统一转换为可计算数值。 */
export function toNumber(
  value: number | string | null | undefined,
): number | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  const numericValue = typeof value === "number" ? value : Number(value);
  return Number.isFinite(numericValue) ? numericValue : null;
}

function padStart(value: number, length = 2): string {
  return String(value).padStart(length, "0");
}

function parseDate(value?: string | null): Date | null {
  if (!value) {
    return null;
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

/** 指数 / 价格格式化，保留指定位数小数并添加千分位。 */
export function formatPrice(
  value: number | string | null | undefined,
  digits = 2,
): string {
  const numericValue = toNumber(value);
  if (numericValue === null) {
    return EMPTY_VALUE;
  }
  return numericValue.toLocaleString("zh-CN", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

/** 带正负号的涨跌额格式化。 */
export function formatSignedNumber(
  value: number | string | null | undefined,
  digits = 2,
): string {
  const numericValue = toNumber(value);
  if (numericValue === null) {
    return EMPTY_VALUE;
  }
  const sign = numericValue > 0 ? "+" : "";
  return `${sign}${numericValue.toLocaleString("zh-CN", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })}`;
}

/** 带正负号的百分比格式化。 */
export function formatSignedPercent(
  value: number | string | null | undefined,
  digits = 2,
): string {
  const numericValue = toNumber(value);
  if (numericValue === null) {
    return EMPTY_VALUE;
  }
  const sign = numericValue > 0 ? "+" : "";
  return `${sign}${numericValue.toFixed(digits)}%`;
}

/** 完整时间格式化：YYYY-MM-DD HH:mm:ss。 */
export function formatDateTime(value?: string | null): string {
  const date = parseDate(value);
  if (!date) {
    return EMPTY_VALUE;
  }
  return `${date.getFullYear()}-${padStart(date.getMonth() + 1)}-${padStart(
    date.getDate(),
  )} ${padStart(date.getHours())}:${padStart(date.getMinutes())}:${padStart(
    date.getSeconds(),
  )}`;
}

/** 新闻时间格式化：当天显示 HH:mm，其余显示 MM/DD。 */
export function formatNewsTime(value?: string | null): string {
  const date = parseDate(value);
  if (!date) {
    return EMPTY_VALUE;
  }
  const now = new Date();
  const isSameDay =
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate();
  if (isSameDay) {
    return `${padStart(date.getHours())}:${padStart(date.getMinutes())}`;
  }
  return `${padStart(date.getMonth() + 1)}/${padStart(date.getDate())}`;
}

/** 计算日期距今天的天数（0 表示今天，负数表示未来日期）。 */
export function getDaysFromToday(value?: string | null): number | null {
  const date = parseDate(value);
  if (!date) {
    return null;
  }
  const today = new Date();
  const startOfToday = new Date(
    today.getFullYear(),
    today.getMonth(),
    today.getDate(),
  ).getTime();
  const startOfDate = new Date(
    date.getFullYear(),
    date.getMonth(),
    date.getDate(),
  ).getTime();
  return Math.round((startOfToday - startOfDate) / 86400000);
}

import {
  NEWS_TAB_TODAY,
  NEWS_TAB_THREE_DAYS,
  type NewsTabKey,
} from "../constants/home";
import type { HotNewsVO } from "../types/home";
import { getDaysFromToday } from "./format";

/**
 * 将后端返回的单列表新闻按发布时间拆分为“当日热点 / 近3日热点”。
 *
 * 后端当前仅提供热门新闻列表，未单独提供近 3 日接口，因此在前端做轻量拆分。
 * 无法解析发布时间的数据默认归入“当日热点”，避免数据丢失。
 */
export function filterNewsForTab(
  news: HotNewsVO[],
  tab: NewsTabKey,
): HotNewsVO[] {
  return news.filter((item) => {
    const days = getDaysFromToday(item.publish_time);

    if (tab === NEWS_TAB_TODAY) {
      return days === null || days <= 0;
    }

    if (tab === NEWS_TAB_THREE_DAYS) {
      return days !== null && days >= 1 && days <= 2;
    }

    return false;
  });
}

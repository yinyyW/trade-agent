import akshare as ak
import time
from http.client import RemoteDisconnected


def get_news():
    try:
        # 同花顺-行业板块列表+实时行情，替代 stock_board_industry_name_em()
        df_news = ak.stock_info_global_em()
        return df_news
    except RemoteDisconnected:
        time.sleep(2)
        return None

df = get_news()
print(df.columns)
print(df.head(5))

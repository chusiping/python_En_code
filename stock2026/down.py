import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

# 1. 设置你的 tushare token
ts.set_token("82b6fc93677908bc41c48b581c815f78efa42a4b40aba0b9548b4d08")
pro = ts.pro_api()

# 2. 计算日期（最近3个月）
end_date = datetime.today().strftime('%Y%m%d')
start_date = (datetime.today() - timedelta(days=90)).strftime('%Y%m%d')

# 3. 获取贵州茅台日线行情
df = pro.daily(
    ts_code='600519.SH',
    start_date=start_date,
    end_date=end_date
)

# 4. 按日期排序
df = df.sort_values('trade_date')

print(df[['trade_date', 'open', 'high', 'low', 'close', 'vol']])

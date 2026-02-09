import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# 1. 设置你的 tushare token
ts.set_token("82b6fc93677908bc41c48b581c815f78efa42a4b40aba0b9548b4d08")
pro = ts.pro_api()

# 2. 读取JSON配置文件
config_file = 'config.json'
if  os.path.exists(config_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
else:
    print("配置文件不存在")
    
days = config.get('days', 90)
stock_codes = config.get('stock_codes', ['600519.SH'])

# 3. 计算日期
end_date = datetime.today().strftime('%Y%m%d')
start_date = (datetime.today() - timedelta(days=days)).strftime('%Y%m%d')

# 4. 获取多个股票的日线行情
for code in stock_codes:
    # 自动添加交易所后缀
    if code.startswith('6'):
        ts_code = code + '.SH'  # 上海交易所
    else:
        ts_code = code + '.SZ'  # 深圳交易所
    
    # 获取股票基本信息（包含名称）
    stock_info = pro.stock_basic(ts_code=ts_code)
    stock_name = stock_info['name'].values[0] if len(stock_info) > 0 else '未知'
    
    print(f"\n{'='*50}")
    print(f"股票代码: {ts_code}")
    print(f"股票名称: {stock_name}")
    print(f"{'='*50}")
    
    df = pro.daily(
        ts_code=ts_code,
        start_date=start_date,
        end_date=end_date
    )
    
    
    # 5. 按日期排序
    df = df.sort_values('trade_date')
    
    print(df[['trade_date', 'open', 'high', 'low', 'close', 'vol']])

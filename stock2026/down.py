import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import json
import os


def load_config(config_file='config.json'):
    """读取JSON配置文件"""
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print("配置文件不存在")
        return {}


def get_date_range(days=90):
    """计算日期范围"""
    end_date = datetime.today().strftime('%Y%m%d')
    start_date = (datetime.today() - timedelta(days=days)).strftime('%Y%m%d')
    return start_date, end_date


def format_ts_code(code):
    """自动添加交易所后缀"""
    if code.startswith('6'):
        return code + '.SH'  # 上海交易所
    else:
        return code + '.SZ'  # 深圳交易所


def fetch_stock_data(pro, ts_code, start_date, end_date):
    """获取股票基本信息和日线行情"""
    stock_info = pro.stock_basic(ts_code=ts_code)
    stock_name = stock_info['name'].values[0] if len(stock_info) > 0 else '未知'
    
    df = pro.daily(
        ts_code=ts_code,
        start_date=start_date,
        end_date=end_date
    )
    df = df.sort_values('trade_date')
    
    return stock_name, df


def display_stock_data(ts_code, stock_name, df):
    """显示股票数据"""
    print(f"\n{'='*50}")
    print(f"股票代码: {ts_code}")
    print(f"股票名称: {stock_name}")
    print(f"{'='*50}")
    print(df[['trade_date', 'open', 'high', 'low', 'close', 'vol']])


def main():
    """主程序"""
    # 设置 tushare token
    ts.set_token("82b6fc93677908bc41c48b581c815f78efa42a4b40aba0b9548b4d08")
    pro = ts.pro_api()
    
    # 读取配置
    config = load_config('config.json')
    days = config.get('days', 90)
    stock_codes = config.get('stock_codes', ['600519.SH'])
    
    # 计算日期
    start_date, end_date = get_date_range(days)
    
    # 获取多个股票的日线行情
    for code in stock_codes:
        ts_code = format_ts_code(code)
        stock_name, df = fetch_stock_data(pro, ts_code, start_date, end_date)
        display_stock_data(ts_code, stock_name, df)


if __name__ == '__main__':
    main()

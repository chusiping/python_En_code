import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import sqlite3

# 全局配置
SAVE_SQLITE = True
TOKEN = "82b6fc93677908bc41c48b581c815f78efa42a4b40aba0b9548b4d08"
CONFIG_FILE = 'config.json'
DB_FILE = 'output/ai_stock.db'


def init_tushare():
    """初始化 tushare API"""
    ts.set_token(TOKEN)
    return ts.pro_api()


def load_config():
    """读取配置文件，不存在则创建默认配置"""
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "days": 90,
            "stock_codes": ["600519", "000858"]
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
        return default_config
    else:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)


def calculate_dates(days):
    """计算开始和结束日期"""
    end_date = datetime.today().strftime('%Y%m%d')
    start_date = (datetime.today() - timedelta(days=days)).strftime('%Y%m%d')
    return start_date, end_date


def get_stock_list(pro):
    """获取股票基本信息列表"""
    try:
        return pro.stock_basic(exchange='', list_status='L', fields='ts_code,name')
    except Exception:
        return None


def normalize_ts_code(code):
    """自动添加交易所后缀"""
    if '.' in code:
        return code
    elif code.startswith('6'):
        return code + '.SH'
    else:
        return code + '.SZ'


def get_stock_name(ts_code, code, stock_list):
    """获取股票名称"""
    if stock_list is not None and not stock_list.empty:
        match = stock_list[stock_list['ts_code'] == ts_code]
        if not match.empty:
            name = match['name'].values[0]
            if name and str(name).strip():
                return name
    return ts_code


def fetch_daily_data(pro, ts_code, start_date, end_date):
    """获取日线行情数据"""
    try:
        # stock_info = pro.stock_basic(ts_code=ts_code)
        # stock_name = stock_info['name'].values[0] if len(stock_info) > 0 else '未知'
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        df = df.sort_values('trade_date')
        return df
    except Exception as e:
        print(f"查询 {ts_code} 时出错: {e}")
        return None


def prepare_dataframe(df, ts_code, stock_name):
    """处理数据框：排序并增加辅助列"""
    df = df.sort_values('trade_date')
    df['ts_code'] = ts_code
    df['name'] = stock_name
    return df


def save_daily_to_db(df, conn):
    """
    将日线 DataFrame 保存到 sqlite
    使用 INSERT OR IGNORE，避免重复数据
    """
    if df is None or df.empty:
        return

    insert_sql = """
    INSERT OR IGNORE INTO stock_daily
    (ts_code, ts_name, trade_date, open, high, low, close, volume, amount)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    data = []
    for _, row in df.iterrows():
        data.append((
            row["ts_code"],
            row["name"],
            row["trade_date"],
            row["open"],
            row["high"],
            row["low"],
            row["close"],
            row["vol"],
            row.get("amount")  # amount 有些接口可能没有
        ))

    cursor = conn.cursor()
    cursor.executemany(insert_sql, data)
    conn.commit()


def process_stock(pro, code,stock_name, start_date, end_date, stock_list, conn):
    """处理单只股票的数据获取和保存"""
    ts_code = normalize_ts_code(code)
    # stock_name = get_stock_name(ts_code, code, stock_list)
    
    df = fetch_daily_data(pro, ts_code, start_date, end_date)

    print(f"\n{'='*50}")
    print(f"股票代码: {ts_code}")
    print(f"股票名称: {stock_name}")
    print(f"{'='*50}")
    
    
    if df is None or df.empty:
        print(f"无 {ts_code} 的日线数据.")
        return
    df = prepare_dataframe(df, ts_code, stock_name)
    save_daily_to_db(df, conn)
    print(f"{ts_code} 数据已写入数据库，共 {len(df)} 条")

def main():
    """主函数"""
    # 初始化
    pro = init_tushare()
    config = load_config()
    conn = sqlite3.connect(DB_FILE)
    
    # 获取配置参数
    days = config.get('days', 90)
    # stock_codes = config.get('stock_codes', ['600519'])
    stock_codes = config.get("stock_codes")
    # 计算日期
    start_date, end_date = calculate_dates(days)
    
    # 获取股票列表
    stock_list = get_stock_list(pro)
    
    # 处理每只股票
    for stock in stock_codes:
        code = stock["code"]
        name = stock["name"]
        process_stock(pro, code,name, start_date, end_date, stock_list, conn)
    
    conn.close()


if __name__ == '__main__':
    main()
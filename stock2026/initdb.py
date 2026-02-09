import sqlite3

DB_PATH = "output/stock.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_stock_daily_table():
    """
    创建股票日线表（如不存在）
    """
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_daily (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts_code TEXT NOT NULL,
        ts_name TEXT,
        trade_date TEXT NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume REAL,
        amount REAL,
        UNIQUE(ts_code, trade_date)
    )
    """)

    conn.commit()
    conn.close()
    print("db生成！")


if __name__ == '__main__':
    init_stock_daily_table()
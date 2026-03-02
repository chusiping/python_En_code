import sqlite3
import os

# 数据库路径改到 config 文件夹下
CONFIG_DIR = "config"
os.makedirs(CONFIG_DIR, exist_ok=True)  # 确保文件夹存在
DB_PATH = os.path.join(CONFIG_DIR, "vehicle_mileage.db")


def init_db():
    """初始化数据库和表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mileage (
            vehicle_id TEXT PRIMARY KEY,
            last_mileage REAL
        )
    """)
    conn.commit()
    conn.close()


def get_last_mileage(vehicle_id: str) -> float:
    """获取车辆上次里程"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT last_mileage FROM mileage WHERE vehicle_id=?", (vehicle_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    return 0.0  # 没有记录则返回 0


def update_mileage(vehicle_id: str, mileage: float):
    """更新车辆里程"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO mileage(vehicle_id, last_mileage) VALUES (?, ?)
        ON CONFLICT(vehicle_id) DO UPDATE SET last_mileage=excluded.last_mileage
    """, (vehicle_id, mileage))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # 测试代码
    init_db()
    vehicle = "CAR123"
    
    print(f"上次里程: {get_last_mileage(vehicle)}")
    
    print("更新里程为 1200.5")
    update_mileage(vehicle, 1200.5)
    
    print(f"更新后里程: {get_last_mileage(vehicle)}")
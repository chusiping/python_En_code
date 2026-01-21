# excel_to_config.py
import pandas as pd
import json
import os
from datetime import datetime

# 仅此一行，全平台有效，0延迟
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 可选：Windows控制台优化（try保护，Linux自动跳过）
try:
    import ctypes
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
except:
    pass  # Linux上自动忽略，无需平台检查

def excel_to_config(excel_path, output_dir="config"):
    """
    将Excel配置转换为JSON配置文件
    """
    # 读取Excel
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"读取Excel失败: {e}")
        return None
    
    print(f"")
    print(f"成功读取Excel，共 {len(df)} 行配置")
    
    # 转换为任务列表
    tasks = []
    for index, row in df.iterrows():
        # 检查是否启用
        enabled = str(row.get('enabled', '是')).strip() in ['是', 'yes', 'true', '1', '启用']
        
        if not enabled:
            print(f"  -{index+1}.　　禁用: {row.get('name', f'行{index+1}')}")
            continue
        
        # 处理日期和时间
        start_date_str = str(row.get('start_date', '')).strip()
        start_time_str = str(row.get('start_time', '')).strip()
        # 合并日期和时间
        schedule_time = None
        schedule_note = None

        if start_date_str and start_time_str:
            try:
                # 合并日期和时间
                datetime_str = f"{start_date_str} {start_time_str}"
                parsed_time = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                # 使用易读的格式，而不是ISO格式
                schedule_time = parsed_time.strftime("%Y-%m-%d %H:%M:%S")  # 改为这个
                schedule_note = f"定时执行于 {schedule_time}"
            except ValueError as e:
                print(f"⚠  第{index+2}行日期时间格式错误: {start_date_str} {start_time_str}")
                schedule_time = None
                schedule_note = "时间不完整"

        task = {
            "name": str(row.get('name', f'任务{index+1}')).strip(),
            "excel_file": str(row.get('excel_file', '')).strip(),
            "server_ip": str(row.get('server_ip', '127.0.0.1')).strip(),
            "server_port": int(row.get('server_port', 8080)),
            "terminal_phone": str(row.get('terminal_phone', '')).strip(),
            # 重要修改：schedule_time 现在是字符串，可能是ISO时间或HH:MM:SS
            # "start_time": str(row.get('start_time', '09:00:00')).strip(),            
            "schedule_time": schedule_time,  # ISO格式的绝对时间或None
            "description": str(row.get('description', '')).strip(),
            "schedule_note": schedule_note
        }
        tasks.append(task)
        print(f"  -{index+1}.添加配置: {task['name']}")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成JSON配置
    config = {
        "version": "1.0",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_excel": os.path.basename(excel_path),
        "tasks": tasks
    }
    
    # 保存JSON文件
    output_file = os.path.join(output_dir, "tasks.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"\n配置已生成: {output_file} 共 {len(tasks)} 个任务")
    return config

def load_config(config_path="config/tasks.json"):
    """
    加载JSON配置文件
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"加载配置: {config_path}")
        print(f"版本: {config.get('version', '未知')}")
        print(f"生成时间: {config.get('generated_at', '未知')}")
        print(f"任务数量: {len(config.get('tasks', []))}")
        
        return config
    
    except FileNotFoundError:
        print(f"配置文件不存在: {config_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"配置文件格式错误: {e}")
        return None

if __name__ == "__main__":
    # 测试：从Excel生成配置
    excel_path = "config.xlsx"
    
    if os.path.exists(excel_path):
        config = excel_to_config(excel_path)
        if config:
            print("\n配置预览:")
            for task in config["tasks"]:  # 显示前3个
                print(f"  - {task['name']}: {task['description']}")
    else:
        print(f"Excel文件不存在: {excel_path}")
        print("请创建: config.xlsx")
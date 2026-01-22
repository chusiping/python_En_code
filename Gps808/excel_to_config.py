
import pandas as pd
import json
import os
from datetime import datetime
import re
import check_config
import sys

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
        else:
            print(f"⚠  日期时间缺失: {start_date_str} {start_time_str}")
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

def validate_task_config(row, index):
    """
    验证任务配置的各个字段
    """
    errors = []
    task = {}
    
    # 2. 验证excel_file
    excel_file = str(row.get('excel_file', '')).strip()
    if not excel_file:
        errors.append("Excel文件路径为空")
    else:
        if not os.path.exists(excel_file):
            errors.append(f"Excel文件不存在")    
    
    # 3. 验证server_ip
    server_ip = str(row.get('server_ip', '')).strip()
    if not server_ip:
        errors.append("服务器IP地址为空")
    else:
        # IP地址格式验证
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_pattern, server_ip):
            errors.append(f"IP地址格式不正确: {server_ip}")
        else:
            # 验证每个部分在0-255之间
            parts = server_ip.split('.')
            for part in parts:
                if not part.isdigit() or int(part) < 0 or int(part) > 255:
                    errors.append(f"IP地址部分超出范围: {part}")
                    break
            task["server_ip"] = server_ip
    
    # 4. 验证server_port
    server_port = row.get('server_port')
    try:
        if server_port is None:
            errors.append("服务器端口为空")
        else:
            port = int(server_port)
            if port < 1 or port > 65535:
                errors.append(f"端口号超出范围(1-65535): {port}")
            else:
                task["server_port"] = port
    except (ValueError, TypeError):
        errors.append(f"端口号格式不正确: {server_port}")
    
    # 5. 验证terminal_phone
    terminal_phone = str(row.get('terminal_phone', '')).strip()
    if not terminal_phone:
        errors.append("终端电话号码为空")
    else:
        # 简单的手机号验证（11位数字）
        if not re.match(r'^\d{11}$', terminal_phone):
            errors.append(f"终端电话号码格式不正确（应为11位数字）: {terminal_phone}")
        else:
            task["terminal_phone"] = terminal_phone
    
    # 6. 验证start_date（来自表格的start_date列）
    start_date_str = str(row.get('start_date', '')).strip()
    if not start_date_str:
        errors.append("开始日期为空")
    else:
        try:
            # 尝试多种日期格式
            date_formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%Y年%m月%d日']
            date_parsed = False
            
            for date_format in date_formats:
                try:
                    start_date = datetime.strptime(start_date_str, date_format)
                    task["start_date"] = start_date.strftime('%Y-%m-%d')
                    date_parsed = True
                    break
                except ValueError:
                    continue
            
            if not date_parsed:
                errors.append(f"开始日期格式不正确: {start_date_str}，期望格式: YYYY-MM-DD")
        except Exception as e:
            errors.append(f"解析开始日期时出错: {start_date_str}, 错误: {e}")
    
    # 7. 验证start_time（来自表格的start_time列）
    start_time_str = str(row.get('start_time', '')).strip()
    if not start_time_str:
        errors.append("开始时间为空")
    else:
        try:
            # 尝试多种时间格式
            time_formats = ['%H:%M:%S', '%H:%M', '%H时%M分%S秒']
            time_parsed = False
            
            for time_format in time_formats:
                try:
                    start_time = datetime.strptime(start_time_str, time_format)
                    task["start_time"] = start_time.strftime('%H:%M:%S')
                    time_parsed = True
                    break
                except ValueError:
                    continue
            
            if not time_parsed:
                errors.append(f"开始时间格式不正确: {start_time_str}，期望格式: HH:MM:SS")
        except Exception as e:
            errors.append(f"解析开始时间时出错: {start_time_str}, 错误: {e}")
    
    # 8. 合并日期和时间（如果有的话）
    if 'start_date' in task and 'start_time' in task:
        try:
            datetime_str = f"{task['start_date']} {task['start_time']}"
            full_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            
            # 检查时间是否已经过去
            now = datetime.now()
            if full_datetime < now:
                errors.append(f"计划时间已经过去: {datetime_str}，当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # task["schedule_time"] = datetime_str
        except Exception as e:
            errors.append(f"合并日期时间时出错: {e}")



if __name__ == "__main__":
    # 测试：从Excel生成配置
    excel_path = "config.xlsx"
    
    # # 进行验证
    try:
        success, tasks, errors = check_config.validate_task_configuration(excel_path)
        
        if not success:
            print("\n程序终止: 配置验证失败")
            sys.exit(1)
        else:
            print("\nconfig.xlsx 配置验证通过，可以继续执行任务调度")
            
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序执行出错: {e}")
        import traceback
        traceback.print_exc()

    if os.path.exists(excel_path):
        config = excel_to_config(excel_path)
        if config:
            print("\n配置预览:")
            for task in config["tasks"]:  # 显示前3个
                print(f"  - {task['name']}: {task['description']}")
    else:
        print(f"Excel文件不存在: {excel_path}")
        print("请创建: config.xlsx")
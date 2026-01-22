import os
import re
import sys
import pandas as pd
from datetime import datetime
import json

def validate_task_configuration(_excel_path):
    """
    完整的任务配置验证函数
    """
    print("=" * 60)
    
    # 1. 查找Excel配置文件
    config_file = _excel_path
    # config_file = find_config_file()
    if not config_file:
        print("✗ 未找到配置文件")
        return False, [], ["未找到配置文件"]
    
    print(f"✓ 找到配置文件: {config_file}")
    
    # 2. 读取Excel文件
    df = read_excel_file(config_file)
    if df is None:
        return False, [], ["无法读取Excel文件"]
    
    # print(f"✓ 成功读取Excel文件")
    print(f"  任务数量: {len(df)}")
    
    # 3. 验证所有任务
    all_errors = []
    validated_tasks = []
    
    for index, row in df.iterrows():
        # print(f"\n验证任务 {index + 1}/{len(df)}...")
        
        # 创建任务字典
        task = create_task_from_row(row, index)
        
        # 验证任务
        errors = validate_task(task)
        
        if errors:
            error_msg = f"任务 '{task.get('name', '未命名')}' 验证失败: {', '.join(errors)}"
            # print(f"✗ {error_msg}")
            all_errors.append(error_msg)
        else:
            print(f"✓ 任务 '{task['name']}' 验证通过")
            validated_tasks.append(task)
    
    # 4. 输出结果
    if all_errors:
        print(f"\n{'='*60}")
        print(f"验证失败！发现 {len(all_errors)} 个错误")
        print(f"{'='*60}")
        for i, error in enumerate(all_errors[:10], 1):
            print(f"{i}. {error}")
        
        if len(all_errors) > 10:
            print(f"... 还有 {len(all_errors) - 10} 个错误未显示")
        
        return False, validated_tasks, all_errors
    else:
        print(f"\n{'='*60}")
        print(f"验证成功！所有 {len(validated_tasks)} 个任务通过验证")
        print(f"{'='*60}")
        
        # 显示验证通过的任务
        # for i, task in enumerate(validated_tasks, 1):
        #     print(f"\n{i}. {task['name']}")
        #     print(f"   文件: {os.path.basename(task['excel_file'])}")
        #     print(f"   服务器: {task['server_ip']}:{task['server_port']}")
        #     print(f"   终端: {task['terminal_phone']}")
        #     if 'schedule_time' in task:
        #         print(f"   计划时间: {task['schedule_time']}")
        
        # 保存验证结果
        # save_validated_tasks(validated_tasks)
        
        return True, validated_tasks, []

def read_excel_file(file_path):
    """
    读取Excel文件
    """
    try:
        # 尝试不同的引擎
        engines = ['openpyxl', None, 'xlrd']
        
        for engine in engines:
            try:
                if engine:
                    df = pd.read_excel(file_path, engine=engine)
                else:
                    df = pd.read_excel(file_path)
                
                # print(f"✓ 使用引擎 {engine if engine else 'auto'} 成功读取")
                return df
            except Exception as e:
                print(f"  引擎 {engine if engine else 'auto'} 失败: {e}")
                continue
        
        return None
    except Exception as e:
        print(f"✗ 读取Excel文件失败: {e}")
        return None

def create_task_from_row(row, index):
    """
    从Excel行数据创建任务字典
    """
    task = {
        "name": get_string_value(row, 'name', f'任务{index+1}'),
        "excel_file": get_string_value(row, 'excel_file', ''),
        "server_ip": get_string_value(row, 'server_ip', ''),
        "server_port": get_numeric_value(row, 'server_port', 0),
        "terminal_phone": clean_phone_number(row.get('terminal_phone', '')),
    }
    
    # 处理日期和时间
    start_date = get_date_value(row, 'start_date')
    start_time = get_time_value(row, 'start_time')
    
    if start_date and start_time:
        try:
            datetime_str = f"{start_date} {start_time}"
            # 验证格式
            datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            task["schedule_time"] = datetime_str
        except ValueError:
            pass  # 如果格式不正确，就不添加schedule_time
    
    # 可选字段
    description = get_string_value(row, 'description', '')
    if description:
        task["description"] = description
    
    return task

def get_string_value(row, column, default=''):
    """
    安全获取字符串值
    """
    try:
        if column in row and pd.notna(row[column]):
            return str(row[column]).strip()
    except:
        pass
    return default

def get_numeric_value(row, column, default=0):
    """
    安全获取数值
    """
    try:
        if column in row and pd.notna(row[column]):
            return int(float(row[column]))
    except:
        pass
    return default

def get_date_value(row, column):
    """
    安全获取日期值
    """
    try:
        if column in row and pd.notna(row[column]):
            value = row[column]
            
            # 如果已经是datetime类型
            if isinstance(value, datetime):
                return value.strftime('%Y-%m-%d')
            
            # 如果是字符串
            value_str = str(value).strip()
            
            # 尝试解析常见格式
            date_formats = [
                '%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d',
                '%Y年%m月%d日', '%Y-%m', '%Y/%m'
            ]
            
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(value_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # 如果是数字（Excel日期序列号）
            try:
                dt = pd.to_datetime(value, unit='D', origin='1899-12-30')
                return dt.strftime('%Y-%m-%d')
            except:
                pass
    except:
        pass
    
    return None

def get_time_value(row, column):
    """
    安全获取时间值
    """
    try:
        if column in row and pd.notna(row[column]):
            value = row[column]
            
            # 如果已经是datetime类型
            if isinstance(value, datetime):
                return value.strftime('%H:%M:%S')
            
            # 如果是字符串
            value_str = str(value).strip()
            
            # 尝试解析常见格式
            time_formats = [
                '%H:%M:%S', '%H:%M', '%H时%M分%S秒',
                '%H%M%S', '%H%M'
            ]
            
            for fmt in time_formats:
                try:
                    dt = datetime.strptime(value_str, fmt)
                    return dt.strftime('%H:%M:%S')
                except ValueError:
                    continue
            
            # 如果是时间部分
            if ':' in value_str:
                parts = value_str.split(':')
                if len(parts) >= 2:
                    hours = parts[0].zfill(2)
                    minutes = parts[1].zfill(2)
                    seconds = parts[2].zfill(2) if len(parts) > 2 else '00'
                    return f"{hours}:{minutes}:{seconds}"
    except:
        pass
    
    return None

def clean_phone_number(phone_value):
    """
    清理手机号，去除.0等
    """
    if pd.isna(phone_value):
        return ''
    
    # 转为字符串
    phone_str = str(phone_value)
    
    # 去除.0
    if phone_str.endswith('.0'):
        phone_str = phone_str[:-2]
    
    # 只保留数字
    digits = ''.join(filter(str.isdigit, phone_str))
    
    # 如果是11位，返回
    if len(digits) == 11:
        return digits
    else:
        # 如果不是11位，返回原始清理后的字符串（用于错误提示）
        return phone_str
    
def validate_task(task):
    """
    验证单个任务
    """
    errors = []
    
    # 1. 验证Excel文件
    excel_file = task.get('excel_file', '')
    if not excel_file:
        errors.append("Excel文件路径为空")
    else:
        # 尝试查找文件
        if not os.path.exists(excel_file):
            # 尝试在excle目录下查找
            filename = os.path.basename(excel_file)
            possible_paths = [
                os.path.join('excle', filename),
                os.path.join('excel', filename),
                filename,
            ]
            
            found = False
            for path in possible_paths:
                if os.path.exists(path):
                    task['excel_file'] = os.path.abspath(path)
                    found = True
                    break
            
            if not found:
                errors.append(f"Excel文件不存在: {excel_file}")
        else:
            task['excel_file'] = os.path.abspath(excel_file)
        
        # 验证文件扩展名
        if not task['excel_file'].lower().endswith(('.xlsx', '.xls')):
            errors.append(f"文件不是Excel格式: {task['excel_file']}")
    
    # 2. 验证IP地址
    ip = task.get('server_ip', '')
    if not ip:
        errors.append("服务器IP地址为空")
    elif not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip):
        errors.append(f"IP地址格式错误: {ip}")
    else:
        # 验证IP各部分
        parts = ip.split('.')
        for part in parts:
            if not part.isdigit() or int(part) < 0 or int(part) > 255:
                errors.append(f"IP地址部分超出范围: {part}")
                break
    
    # 3. 验证端口
    port = task.get('server_port', 0)
    if port < 1 or port > 65535:
        errors.append(f"端口号无效: {port}")
    
    # 4. 验证电话号码
    phone = task.get('terminal_phone', '')
    if not phone:
        errors.append("终端电话号码为空")
    elif not re.match(r'^\d{11}$', phone):
        errors.append(f"电话号码格式错误（需要11位数字）: {phone}")
    
    # 5. 验证计划时间
    if 'schedule_time' in task:
        try:
            schedule_dt = datetime.strptime(task['schedule_time'], '%Y-%m-%d %H:%M:%S')
            if schedule_dt < datetime.now():
                errors.append(f"  警告: 计划时间已过: {task['schedule_time']}")
                # print(f"  警告: 计划时间已过: {task['schedule_time']}")
        except ValueError:
            errors.append(f"计划时间格式错误: {task['schedule_time']}")
    
    return errors

def main():
    """
    主函数
    """
    excel_path = "config.xlsx"
    try:
        success, tasks, errors = validate_task_configuration(excel_path)
        
        if not success:
            print("\n程序终止: 配置验证失败")
        else:
            print("\n配置验证通过，可以继续执行任务调度")
            return tasks
            
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    tasks = main()

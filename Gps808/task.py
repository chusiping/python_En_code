import subprocess
import time
from datetime import datetime
import multiprocessing
import os
import argparse
import excel_to_config
import json
import threading
from concurrent.futures import ThreadPoolExecutor


# 仅此一行，全平台有效，0延迟
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 可选：Windows控制台优化（try保护，Linux自动跳过）
try:
    import ctypes
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
except:
    pass  # Linux上自动忽略，无需平台检查


# 任务配置：每个任务对应一个main.py实例

SERVER_IP = '14.23.86.188'              # 市平台 120.197.38.48  测试平台 14.23.86.188 
SERVER_PORT = 6608                      # 25209   
# SEND_TO_SERVER = False                

parser = argparse.ArgumentParser(description='')
parser.add_argument('--send', dest='is_SEND', action='store_true',help='真实发送数据')
parser.add_argument('--no-send', dest='is_SEND', action='store_false',help='测试模式不实际发送')
parser.set_defaults(SEND_TO_SERVER=False)  # 默认值
args = parser.parse_args()
SEND_TO_SERVER =  args.is_SEND          # 是否真发送

# 全局变量
active_tasks = []  # 存储当前正在运行的任务
running_processes = []  # 存储正在运行的进程
task_lock = threading.Lock()  # 线程锁

# 调试时才使用写死的Tasks
# TASKS = [
#     {
#         "name": "任务1-车队A",
#         "excel_file": r"excle\轨迹列表_A.xlsx",  # 完整路径
#         "server_ip": SERVER_IP,
#         "server_port": SERVER_PORT,
#         "terminal_phone": "13301110130",
#         "start_time": "15:50:50",  # 每天开始时间
#         "description": "处理车队A的数据"
#     },
#     {
#         "name": "任务2-车队B", 
#         "excel_file": r"excle\轨迹列表_B.xlsx",
#         "server_ip": SERVER_IP,
#         "server_port": SERVER_PORT, 
#         "terminal_phone": "13301110130",
#         "start_time": "09:30:00",
#         "description": "处理车队B的数据"
#     }
#     # 添加更多任务...
# ]

def load_tasks_from_json(json_file="config/tasks.json"):
    """
    直接从JSON文件加载任务配置
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        tasks = config.get("tasks", [])
        print(f"从 {json_file} 加载了 {len(tasks)} 个任务")
        return tasks
        
    except FileNotFoundError:
        print(f"配置文件不存在: {json_file}")
        print(f"请手动创建 {json_file} 文件")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON格式错误: {e}")
        print(f"请检查 {json_file} 文件的JSON语法")
        return []
    except Exception as e:
        print(f"加载配置失败: {e}")
        return []


def run_main_process(task_config, log_dir="logs"):
    """
    运行单个main.py进程
    """
    task_name = task_config["name"]
    excel_file = task_config["excel_file"]
    phone = task_config["terminal_phone"]
    server_ip = task_config["server_ip"]
    server_port = task_config["server_port"]
    
    encoding = 'utf-8'  # 固定UTF-8
    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    # 生成日志文件名（带时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{task_name}_{timestamp}.log")

    
    # 构建命令行参数
    cmd = [
        "python", "main_v2.py",
        "--excel", rf'"{excel_file}"',
        "--phone", str(phone),
        "--server-ip", str(server_ip) ,
        "--server-port",str(server_port) ,
    ]
    if SEND_TO_SERVER:
        cmd.append("--send")  # 添加 --send 参数
    
    # print(cmd) 
    # return

    print(f"[{datetime.now()}] 启动任务: {task_name}")
    # print(f"  统一编码: {encoding}")
    # print(f"  Excel文件: {excel_file}")
    # print(f"  参数: {phone} - {server_ip} - {server_port}")
    # print(f"  日志: {log_file}")
    # print(f"  命令: {' '.join(cmd)}")
    
    # 执行命令，重定向输出到日志文件
    # with open(log_file, 'w', encoding=encoding) as f:
    #     f.write(f"任务开始: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n")
    #     f.write(f"任务名称: {task_name}\n")
    #     f.write(f"Excel文件: {excel_file}\n")
    #     f.write(f"参数: {phone} - {server_ip} - {server_port}\n")
    #     f.write("-" * 50 + "\n")
    #     f.flush()  # 立即写入

    # 改写
    with open(log_file, 'w', encoding=encoding) as f:
        f.write("-" * 50 + "\n")
        f.write(f"{task_name}任务开始: {phone}-{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"命令: {' '.join(cmd)}")
        f.flush()  # 立即写入
        
        # 执行main.py
        process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding=encoding,  # 关键：使用UTF-8，不是system_encoding
                bufsize=1,
                cwd=os.path.dirname(__file__),
                # 传递环境变量，确保子进程也使用UTF-8
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
            )
        
        # 实时输出并记录日志
        for line in process.stdout:
                line = line.rstrip('\n')  # 移除换行符
                print(f"[{task_name}] {line}")
                f.write(line + '\n')
                f.flush()
    
    # 等待进程结束
    return_code = process.wait()
    
    with open(log_file, 'a', encoding=encoding) as f:
        f.write(f"\n{task_name}任务结束: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"退出代码: {return_code}\n")
    
    print(f"[{datetime.now()}] 任务完成: {task_name}, 退出代码: {return_code}")
    return return_code

def start_task_if_time(task):
    """
    检查并启动任务（如果时间到了）
    """
    if not task.get("schedule_time"):
        return False
    
    now = datetime.now()
    target_time_str = task["schedule_time"]
    
    # 将配置时间转换为今天的datetime对象
    target_time = datetime.strptime(target_time_str, "%Y-%m-%d %H:%M:%S")
    target_datetime = now.replace(hour=target_time.hour,  minute=target_time.minute,second=target_time.second, microsecond=0)
    
    # 如果配置时间已经过去（在今天），检查是否已经执行过
    # if target_datetime <= now:
    if target_datetime:# 测试的
        # 检查任务是否已经在运行列表中
        with task_lock:
            if task not in active_tasks:
                # 添加到运行中任务列表（但是并不立即执行）
                active_tasks.append(task)
                return True
    return False

def schedule_tasks(tasks):
    """
    调度任务：每隔5秒检查时间并启动符合条件的任务
    """
    print(f"[{datetime.now()}] 开始任务调度，共 {len(tasks)} 个任务")
    
    # 创建线程池用于并发执行任务
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = []
        
        try:
            while True: # 间隔5秒比对一次时间
                # 检查所有任务
                for task in tasks:
                    # 如果任务已经在运行中，跳过
                    with task_lock:
                        if task in active_tasks:
                            continue
                    
                    # 检查是否到达执行时间
                    if start_task_if_time(task):
                        print(f"[{datetime.now()}] 启动任务: {task['name']}")
                        
                        # 使用线程池提交任务
                        future = executor.submit(run_main_process, task)
                        futures.append((task['name'], future))
                
                # 显示当前状态
                with task_lock:
                    running_count = len(active_tasks)
                    pending_count = len(tasks) - running_count
                    print(f"[{datetime.now()}] 状态: 运行中 {running_count} | 等待中 {pending_count}")
                
                # 每隔5秒检查一次
                time.sleep(5)
                
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] 接收到中断信号，停止调度...")
            
            # 等待所有任务完成
            print(f"[{datetime.now()}] 等待 {len(futures)} 个任务完成...")
            for task_name, future in futures:
                try:
                    future.result(timeout=10)  # 等待10秒
                    print(f"[{datetime.now()}] 任务 {task_name} 已完成")
                except Exception as e:
                    print(f"[{datetime.now()}] 任务 {task_name} 出错: {e}")

def main():
    """
    主函数
    """
    # 加载任务配置
    TASKS = load_tasks_from_json("config/tasks.json")
    if not TASKS:
        print("没有可执行的任务，程序退出")
        return
    
    # print("=" * 60 + "\nJT808 任务调度器启动\n" + 
    #       f"系统时间: {datetime.now()}\n" + 
    #       f"CPU核心数: {multiprocessing.cpu_count()}\n" + 
    #       f"总任务数: {len(TASKS)}\n" + 
    #       "=" * 60)
    
    # 显示所有任务及其计划时间
    print("\n任务列表:")
    for i, task in enumerate(TASKS, 1):
        schedule_time = task.get("schedule_time", "立即执行")
        print(f"  {i}. {task['name']} - 计划时间: {schedule_time}")
    
    print("\n调度器开始运行，每隔5秒检查一次任务时间...")
    print("按 Ctrl+C 停止程序\n")
    
    # 开始调度任务
    schedule_tasks(TASKS)

if __name__ == "__main__":
    main()
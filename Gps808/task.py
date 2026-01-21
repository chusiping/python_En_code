import subprocess
import time
from datetime import datetime
import multiprocessing
import os
import argparse
import excel_to_config
import json

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
        "python", "main.py",
        "--excel", excel_file,
        "--phone", str(phone),
        "--server-ip", str(server_ip) ,
        "--server-port",str(server_port) ,
    ]
    if SEND_TO_SERVER:
        cmd.append("--send")  # 添加 --send 参数
    
    # print(cmd) 
    # return

    print(f"[{datetime.now()}] 启动任务: {task_name}")
    print(f"  统一编码: {encoding}")
    print(f"  Excel文件: {excel_file}")
    print(f"  参数: {phone} - {server_ip} - {server_port}")
    print(f"  日志: {log_file}")
    print(f"  命令: {' '.join(cmd)}")
    
    # 执行命令，重定向输出到日志文件
    with open(log_file, 'w', encoding=encoding) as f:
        f.write(f"任务开始: {datetime.now()}\n")
        f.write(f"任务名称: {task_name}\n")
        f.write(f"Excel文件: {excel_file}\n")
        f.write(f"参数: {phone} - {server_ip} - {server_port}\n")
        f.write("-" * 50 + "\n")
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
        f.write(f"\n任务结束: {datetime.now()}\n")
        f.write(f"退出代码: {return_code}\n")
    
    print(f"[{datetime.now()}] 任务完成: {task_name}, 退出代码: {return_code}")
    return return_code

def wait_until(target_time, check_interval=1):
    """
    等待到指定时间，显示动态倒计时
    """   
    now = datetime.now()
    target = datetime.strptime(target_time, "%H:%M:%S")
    target = now.replace(hour=target.hour, minute=target.minute, second=target.second)
    
    if target < now:
        target = target.replace(day=target.day + 1)
    
    wait_seconds = (target - now).total_seconds()
    
    # 如果等待时间很长（超过10秒），显示动态倒计时
    if wait_seconds > 10:
        print(f"\n等待到 {target_time}...")
        print("-" * 40)
        
        last_update = 0
        while wait_seconds > 0:
            current_time = time.time()
            
            # 每1秒更新一次显示（不要更新太频繁）
            if current_time - last_update >= 1:
                # 计算剩余时间
                hours = int(wait_seconds // 3600)
                minutes = int((wait_seconds % 3600) // 60)
                seconds = int(wait_seconds % 60)
                
                # 清除当前行，重新输出
                print(f"\r剩余时间: {hours:02d}:{minutes:02d}:{seconds:02d} | "
                      f"预计开始: {target.strftime('%Y-%m-%d %H:%M:%S')}", 
                      end="", flush=True)
                
                last_update = current_time
            
            # 小睡一下，减少CPU占用
            time.sleep(0.1)
            wait_seconds -= 0.1
        
        print()  # 换行
    else:
        # 短时间等待直接sleep
        time.sleep(wait_seconds)
    
def main():

    # 使用配置文件和"调试时才使用写死的Tasks"二选一
    TASKS = load_tasks_from_json("config/tasks.json")
    if not TASKS:
        print("没有可执行的任务，程序退出")
        return

    """
    主调度函数
    """
    print("=" * 60)
    print("JT808 多任务调度器启动")
    print(f"系统时间: {datetime.now()}")
    print(f"CPU核心数: {multiprocessing.cpu_count()}")
    print("=" * 60)
    
    processes = []
    
    try:
        for task in TASKS:
            # 等待到指定时间
            # if task.get("start_time"):
            #     wait_until(task["start_time"])
            
            # 使用多进程并行执行
            process = multiprocessing.Process(
                target=run_main_process,
                args=(task,),
                name=task["name"]
            )
            
            process.start()
            processes.append(process)
            print(f"")
            print(f"已启动进程: {task['name']} (PID: {process.pid})")
            
            # 可以添加启动间隔
            time.sleep(0.1)  # 间隔0.1秒启动下一个
        
        # 等待所有进程完成
        print("\n等待所有任务完成...")
        for process in processes:
            process.join()
            print(f"进程 {process.name} 已完成")
    
    except KeyboardInterrupt:
        print("\n接收到中断信号，正在停止所有进程...")
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join()
                print(f"已终止进程: {process.name}")
    
    print("\n所有任务执行完毕！")

if __name__ == "__main__":
    main()
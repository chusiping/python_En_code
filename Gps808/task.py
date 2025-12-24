import subprocess
import time
from datetime import datetime
import multiprocessing
import os

# 任务配置：每个任务对应一个main.py实例
TASKS = [
    {
        "name": "任务1-车队A",
        "excel_file": r"E:\data\fleet_a.xlsx",  # 完整路径
        "params": {
            "server_ip": "192.168.1.100",
            "server_port": "8080",
            "terminal_prefix": "A"
        },
        "start_time": "09:00:00",  # 每天开始时间
        "description": "处理车队A的数据"
    },
    {
        "name": "任务2-车队B", 
        "excel_file": r"E:\data\fleet_b.xlsx",
        "params": {
            "server_ip": "192.168.1.101",
            "server_port": "8081", 
            "terminal_prefix": "B"
        },
        "start_time": "09:30:00",
        "description": "处理车队B的数据"
    },
    # 添加更多任务...
]

def run_main_process(task_config, log_dir="logs"):
    """
    运行单个main.py进程
    """
    task_name = task_config["name"]
    excel_file = task_config["excel_file"]
    params = task_config["params"]
    
    # 创建日志目录
    os.makedirs(log_dir, exist_ok=True)
    
    # 生成日志文件名（带时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{task_name}_{timestamp}.log")
    
    # 构建命令行参数
    cmd = [
        "python", "main.py",
        "--excel", excel_file,
        "--server-ip", params["server_ip"],
        "--server-port", params["server_port"],
        "--prefix", params["terminal_prefix"]
    ]
    
    print(f"[{datetime.now()}] 启动任务: {task_name}")
    print(f"  Excel文件: {excel_file}")
    print(f"  参数: {params}")
    print(f"  日志: {log_file}")
    
    # 执行命令，重定向输出到日志文件
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"任务开始: {datetime.now()}\n")
        f.write(f"任务名称: {task_name}\n")
        f.write(f"Excel文件: {excel_file}\n")
        f.write(f"参数: {params}\n")
        f.write("-" * 50 + "\n")
        
        # 执行main.py
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8'
        )
        
        # 实时输出并记录日志
        for line in process.stdout:
            print(f"[{task_name}] {line}", end='')
            f.write(line)
    
    # 等待进程结束
    return_code = process.wait()
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n任务结束: {datetime.now()}\n")
        f.write(f"退出代码: {return_code}\n")
    
    print(f"[{datetime.now()}] 任务完成: {task_name}, 退出代码: {return_code}")
    return return_code

def wait_until(target_time):
    """
    等待到指定时间
    """
    now = datetime.now()
    target = datetime.strptime(target_time, "%H:%M:%S")
    target = now.replace(hour=target.hour, minute=target.minute, second=target.second)
    
    if target < now:
        # 如果目标时间已过，推到明天
        target = target.replace(day=target.day + 1)
    
    wait_seconds = (target - now).total_seconds()
    print(f"等待 {wait_seconds:.1f} 秒直到 {target_time}...")
    time.sleep(wait_seconds)
    
def main():
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
            if task.get("start_time"):
                wait_until(task["start_time"])
            
            # 使用多进程并行执行
            process = multiprocessing.Process(
                target=run_main_process,
                args=(task,),
                name=task["name"]
            )
            
            process.start()
            processes.append(process)
            print(f"已启动进程: {task['name']} (PID: {process.pid})")
            
            # 可以添加启动间隔
            time.sleep(2)  # 间隔2秒启动下一个
        
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
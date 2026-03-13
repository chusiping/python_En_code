import subprocess
import time
from datetime import datetime
import os
import argparse
import json
import logging

# ==================== 环境设置 ====================
os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    import ctypes
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
except Exception:
    pass

# ==================== 参数解析 ====================
parser = argparse.ArgumentParser(description='Windows 稳定型子进程调度器（无线程）')
parser.add_argument('--send', dest='is_SEND', action='store_true', help='真实发送数据')
parser.add_argument('--no-send', dest='is_SEND', action='store_false', help='测试模式不实际发送')
parser.add_argument('--config', dest='config_file', type=str, help='JSON配置文件路径')
parser.set_defaults(is_SEND=False)
args = parser.parse_args()

# 如果没有指定配置文件，提示用户选择
if args.config_file is None:
    print("请指定JSON配置文件路径")
    config_dir = "config"
    if os.path.exists(config_dir):
        print(f"\n{config_dir} 目录下可用的JSON文件:")
        for f in os.listdir(config_dir):
            if f.endswith(".json"):
                print(f"  - {config_dir}/{f}")
    else:
        print(f"目录 {config_dir} 不存在")
    exit(1)

TASK_FILE = args.config_file

# 验证文件是否存在
if not os.path.exists(TASK_FILE):
    print(f"错误: 配置文件不存在 - {TASK_FILE}")
    exit(1)

SEND_TO_SERVER = args.is_SEND

# ==================== 配置 ====================
LOG_DIR = 'logs'
CHECK_INTERVAL = 30  # 从5面改为30，减少日志压力
MAX_CONCURRENT_PROCESSES = 50

# ==================== 参数解析 ====================
def load_tasks(now=None):
    """
    加载任务，只保留未来将要执行的任务（schedule_time > now）
    """
    if now is None:
        now = datetime.now()

    with open(TASK_FILE, 'r', encoding='utf-8') as f:
        tasks = json.load(f).get('tasks', [])

    future_tasks = []
    for task in tasks:
        schedule_time = task.get('schedule_time')
        if not schedule_time:
            continue  # 没有时间的任务忽略
        target = datetime.strptime(schedule_time, '%Y-%m-%d %H:%M:%S')
        if target > now:
            future_tasks.append(task)

    return future_tasks

# ==================== 时间判断 ====================
def is_time_to_run(task, now):
    """
    判断任务是否到执行时间
    """
    schedule_time = task.get('schedule_time')
    if not schedule_time:
        return False
    target = datetime.strptime(schedule_time, '%Y-%m-%d %H:%M:%S')
    return now >= target

# ==================== 启动子进程 ====================
def start_process(task):
    os.makedirs(LOG_DIR, exist_ok=True)

    task_name = task['name']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    parent_pid = os.getpid()
    log_path = os.path.join(LOG_DIR, f"pid{parent_pid}_{timestamp}_{task_name}.log")

    cmd = [
        'python', '-u', 'main_v2.py',
        '--excel', task['excel_file'],
        '--phone', str(task['terminal_phone']),
        '--server-ip', task['server_ip'],
        '--server-port', str(task['server_port'])
    ]

    if SEND_TO_SERVER:
        cmd.append('--send')

    log_file = open(log_path, 'w', encoding='utf-8')
    log_file.write(f"[{datetime.now()}] START {task_name}\n")
    log_file.write(f"CMD: {' '.join(cmd)}\n")
    log_file.flush()

    proc = subprocess.Popen(
        cmd,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        cwd=os.path.dirname(__file__),
        env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
    )

    task['_process'] = proc
    task['_log_file'] = log_file
    task['_status'] = 'RUNNING'
    task['_started_at'] = datetime.now()

    print(f"[{datetime.now()}] ▶ 启动任务 {task_name} (PID={proc.pid})")

# ==================== 主调度循环 ====================
def scheduler_loop(tasks):
    # 使用logging.info替代print
    logging.info(f"调度器启动，共 {len(tasks)} 个任务")

    for task in tasks:
        task['_status'] = 'PENDING'
        task['_process'] = None
        task['_started_at'] = None

    while True:
        now = datetime.now()

        # 1. 回收已完成子进程
        running_tasks = [t for t in tasks if t['_status'] == 'RUNNING']
        for task in running_tasks:
            proc = task['_process']
            if proc.poll() is not None:  # 已结束
                task['_status'] = 'FINISHED'
                task['_finished_at'] = datetime.now()
                task['_log_file'].write(f"[{datetime.now()}] FINISHED rc={proc.returncode}\n")
                task['_log_file'].close()
                logging.info(f"[{datetime.now()}] ✔ 任务完成 {task['name']} (rc={proc.returncode})")

        # 2. 启动到点任务
        running_count = len([t for t in tasks if t['_status'] == 'RUNNING'])
        available_slots = MAX_CONCURRENT_PROCESSES - running_count

        if available_slots > 0:
            for task in tasks:
                if task['_status'] == 'PENDING' and is_time_to_run(task, now):
                    if available_slots <= 0:
                        break
                    start_process(task)
                    available_slots -= 1

        # 3. 打印状态
        pending_count = len([t for t in tasks if t['_status'] == 'PENDING'])
        running_count = len([t for t in tasks if t['_status'] == 'RUNNING'])
        finished_count = len([t for t in tasks if t['_status'] == 'FINISHED'])

        logging.info(f"[{now}] 状态 | 等待:{pending_count} 运行:{running_count} 完成:{finished_count}")

        if finished_count == len(tasks):
            logging.info("[{datetime.now()}]🎉 所有任务完成，调度器退出")
            break

        time.sleep(CHECK_INTERVAL)

# ==================== main ====================
def main():
    os.makedirs(LOG_DIR, exist_ok=True)
    current_pid = os.getpid()
    LOG_FILENAME = f"logs/run_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}_pid{current_pid}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(LOG_FILENAME, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    now = datetime.now()
    tasks = load_tasks(now=now)
    if not tasks:
        logging.info("没有未来任务，退出")
        return

    logging.info("任务列表（只显示未来任务）:")
    for i, t in enumerate(tasks, 1):
        logging.info(f"  {i}. {t['name']} @ {t.get('schedule_time')}")

    scheduler_loop(tasks)

if __name__ == '__main__':
    main()

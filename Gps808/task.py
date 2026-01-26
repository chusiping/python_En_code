import subprocess
import time
from datetime import datetime
import os
import argparse
import json

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
parser.set_defaults(is_SEND=False)
args = parser.parse_args()
SEND_TO_SERVER = args.is_SEND

# ==================== 配置 ====================
TASK_FILE = 'config/tasks.json'
LOG_DIR = 'logs'
CHECK_INTERVAL = 5  # 秒
MAX_CONCURRENT_PROCESSES = 50

# ==================== 任务加载 ====================
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
    log_path = os.path.join(LOG_DIR, f"{task_name}_{timestamp}.log")

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
    print(f"[{datetime.now()}] 调度器启动，共 {len(tasks)} 个任务")

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
                print(f"[{datetime.now()}] ✔ 任务完成 {task['name']} (rc={proc.returncode})")

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

        print(f"[{now}] 状态 | 等待:{pending_count} 运行:{running_count} 完成:{finished_count}")

        if finished_count == len(tasks):
            print(f"[{datetime.now()}] 🎉 所有任务完成，调度器退出")
            break

        time.sleep(CHECK_INTERVAL)

# ==================== main ====================
def main():
    now = datetime.now()
    tasks = load_tasks(now=now)
    if not tasks:
        print("没有未来任务，退出")
        return

    print("任务列表（只显示未来任务）:")
    for i, t in enumerate(tasks, 1):
        print(f"  {i}. {t['name']} @ {t.get('schedule_time')}")

    scheduler_loop(tasks)

if __name__ == '__main__':
    main()

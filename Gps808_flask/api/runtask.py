from flask import Blueprint, request, jsonify, session, redirect, Response
import subprocess
import os
import uuid
import signal
import psutil
from time import strftime

runtask_bp = Blueprint('runtask', __name__)

CONFIG_DIR = 'config'
TEMP_DIR = 'temp'

def get_unique_filename(directory, filename):
    if not os.path.exists(os.path.join(directory, filename)):
        return filename
    
    name, ext = os.path.splitext(filename)
    counter = 1
    while True:
        new_filename = f"{name}({counter}){ext}"
        if not os.path.exists(os.path.join(directory, new_filename)):
            return new_filename
        counter += 1

running_processes = {}
completed_tasks = []

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/B6nM9qW2eR4tY7uI8oP0lK')
        return f(*args, **kwargs)
    return decorated_function

@runtask_bp.route('/runtask', methods=['POST'])
@login_required
def run_task():
    data = request.json
    filename = data.get('file', '')
    send = data.get('send', False)
    
    if not filename:
        return jsonify({'success': False, 'message': '请选择配置文件'})
    
    filepath = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'message': '配置文件不存在'})
    
    task_id = str(uuid.uuid4())
    mode = '--send' if send else '--no-send'
    cmd = f'python task.py --config {filepath} {mode}'
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    
    def generate():
        process = None
        return_code = -1
        try:
            yield f"[TASK_ID:{task_id}]\n"
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding='utf-8',
                errors='replace',
                cwd=project_root,
                shell=True,
                env=env
            )
            
            yield f"[PID:{process.pid}]\n"
            running_processes[task_id] = process
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    yield line
            
            process.stdout.close()
            return_code = process.wait() if process else -1
            
        except Exception as e:
            yield f"执行出错: {str(e)}\n"
        finally:
            if process:
                try:
                    if task_id in running_processes:
                        del running_processes[task_id]
                    completed_tasks.append({
                        'id': task_id,
                        'pid': process.pid,
                        'return_code': return_code,
                        'finished_at': strftime('%Y-%m-%d %H:%M:%S')
                    })
                    if len(completed_tasks) > 50:
                        completed_tasks.pop(0)
                except:
                    pass
    
    return Response(generate(), mimetype='text/plain; charset=utf-8')

@runtask_bp.route('/runtask/stop/<task_id>', methods=['POST'])
@login_required
def stop_task(task_id):
    if task_id in running_processes:
        process = running_processes[task_id]
        try:
            import sys
            if sys.platform == 'win32':
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(process.pid)])
            else:
                process.terminate()
            return jsonify({'success': True, 'message': '任务已停止'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    return jsonify({'success': False, 'message': '任务不存在或已结束'})

@runtask_bp.route('/runtask/status', methods=['GET'])
@login_required
def get_tasks():
    tasks = []
    for tid, proc in running_processes.items():
        tasks.append({'id': tid, 'pid': proc.pid, 'running': proc.poll() is None})
    return jsonify(tasks)

@runtask_bp.route('/runtask/processes', methods=['GET'])
@login_required
def get_running_processes():
    current_pid = os.getpid()
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                cmd_str = ' '.join(cmdline) if cmdline else ''
                if 'task.py' in cmd_str:
                    processes.append({
                        'pid': proc.info['pid'],
                        'cmd': cmd_str
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return jsonify(processes)

@runtask_bp.route('/runtask/kill', methods=['POST'])
@login_required
def kill_by_pid():
    data = request.json
    pid = data.get('pid')
    if not pid:
        return jsonify({'success': False, 'message': '请提供PID'})
    try:
        import sys
        if sys.platform == 'win32':
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(pid)])
        else:
            os.kill(int(pid), signal.SIGTERM)
        return jsonify({'success': True, 'message': f'进程 {pid} 已终止'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@runtask_bp.route('/runtask/logs', methods=['GET'])
@login_required
def get_log_files():
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        return jsonify([])
    files = sorted([f for f in os.listdir(log_dir) if f.endswith('.log')], reverse=True)
    return jsonify(files)

@runtask_bp.route('/runtask/logs/<filename>', methods=['GET'])
@login_required
def get_log_content(filename):
    log_path = os.path.join('logs', filename)
    if not os.path.exists(log_path):
        return jsonify({'success': False, 'message': '文件不存在'})
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'success': True, 'content': content})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@runtask_bp.route('/runtask/logs/<filename>', methods=['DELETE'])
@login_required
def delete_log_file(filename):
    import shutil
    log_path = os.path.join('logs', filename)
    if not os.path.exists(log_path):
        return jsonify({'success': False, 'message': '文件不存在'})
    try:
        os.makedirs(TEMP_DIR, exist_ok=True)
        unique_filename = get_unique_filename(TEMP_DIR, filename)
        temp_path = os.path.join(TEMP_DIR, unique_filename)
        shutil.move(log_path, temp_path)
        return jsonify({'success': True, 'message': f'文件已重命名为 {unique_filename} 移动到 temp'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

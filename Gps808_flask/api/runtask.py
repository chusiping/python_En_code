from flask import Blueprint, request, jsonify, session, redirect, Response
import subprocess
import os
import uuid
import signal

runtask_bp = Blueprint('runtask', __name__)

CONFIG_DIR = 'config'

running_processes = {}

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
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
            
            running_processes[task_id] = process
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    yield line
            
            process.stdout.close()
            process.wait()
            
        except Exception as e:
            yield f"执行出错: {str(e)}\n"
        finally:
            if task_id in running_processes:
                del running_processes[task_id]
    
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
        tasks.append({'id': tid, 'running': proc.poll() is None})
    return jsonify(tasks)

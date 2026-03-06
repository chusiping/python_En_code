from flask import Blueprint, request, jsonify, session, redirect, Response
import subprocess
import os

runtask_bp = Blueprint('runtask', __name__)

CONFIG_DIR = 'config'

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
    
    mode = '--send' if send else '--no-send'
    cmd = f'chcp 65001 >nul && python task.py --config {filepath} {mode}'
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def generate():
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding='utf-8',
                errors='replace',
                cwd=project_root,
                shell=True
            )
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    yield line
            
            process.stdout.close()
            process.wait()
            
        except Exception as e:
            yield f"执行出错: {str(e)}\n"
    
    return Response(generate(), mimetype='text/plain; charset=utf-8')

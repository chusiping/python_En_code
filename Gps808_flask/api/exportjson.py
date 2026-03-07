from flask import Blueprint, request, jsonify, session, redirect, Response
import subprocess
import os
import shutil

export_bp = Blueprint('export', __name__)

CONFIG_DIR = 'config'
TEMP_DIR = 'temp'

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return jsonify({'success': False, 'message': '请先登录'})
        if session.get('username') != 'admin':
            return jsonify({'success': False, 'message': '只有管理员可以执行此操作'})
        return f(*args, **kwargs)
    return decorated_function

@export_bp.route('/exportjson', methods=['POST'])
@login_required
def export_json():
    data = request.json
    filename = data.get('file', '')
    
    if not filename:
        return jsonify({'success': False, 'message': '请选择文件'})
    
    filepath = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'message': '文件不存在'})
    
    cmd = ['chcp', '65001', '>', 'nul', '&&', 'python', 'excel_to_config.py', filepath]
    
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
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
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

@export_bp.route('/json/<filename>', methods=['DELETE'])
@admin_required
def delete_json_file(filename):
    filepath = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'message': '文件不存在'})
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    dest_path = os.path.join(TEMP_DIR, filename)
    if os.path.exists(dest_path):
        return jsonify({'success': False, 'message': 'temp 文件夹中已存在同名文件'})
    try:
        shutil.move(filepath, dest_path)
        return jsonify({'success': True, 'message': '文件已移动到 temp 文件夹'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

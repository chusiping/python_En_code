from flask import Blueprint, request, jsonify, session, redirect, Response
import subprocess
import os
import shutil

export_bp = Blueprint('export', __name__)

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

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/B6nM9qW2eR4tY7uI8oP0lK')
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
    is_buchaun = data.get('is_buchaun', False)

    if not filename:
        return jsonify({'success': False, 'message': '请选择文件'})

    filepath = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'message': '文件不存在'})

    cmd = ['chcp', '65001', '>', 'nul', '&&', 'python', 'excel_to_config.py', filepath, str(is_buchaun)]
    
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
    unique_filename = get_unique_filename(TEMP_DIR, filename)
    dest_path = os.path.join(TEMP_DIR, unique_filename)
    try:
        shutil.move(filepath, dest_path)
        return jsonify({'success': True, 'message': f'文件已重命名为 {unique_filename} 移动到 temp 文件夹'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

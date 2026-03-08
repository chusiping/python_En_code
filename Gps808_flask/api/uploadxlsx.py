from flask import Blueprint, request, jsonify, session, redirect
import os
from datetime import datetime
import re

upload_bp = Blueprint('upload', __name__)

UPLOAD_FOLDER = 'excle'
TEMP_FOLDER = 'temp'
CONFIG_DIR = 'config'

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

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/B6nM9qW2eR4tY7uI8oP0lK')
        return f(*args, **kwargs)
    return decorated_function

@upload_bp.route('/xlsx/list', methods=['GET'])
@login_required
def list_xlsx_files():
    if not os.path.exists(UPLOAD_FOLDER):
        return jsonify([])
    
    files = []
    for f in os.listdir(UPLOAD_FOLDER):
        if f.endswith(('.xlsx', '.xls')):
            filepath = os.path.join(UPLOAD_FOLDER, f)
            stat = os.stat(filepath)
            files.append({
                'name': f,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    return jsonify(files)

@upload_bp.route('/xlsx/delete', methods=['POST'])
@login_required
def delete_xlsx_file():
    filename = request.json.get('filename')
    if not filename:
        return jsonify({'success': False, 'message': '文件名不能为空'})
    
    src_filepath = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(src_filepath):
        return jsonify({'success': False, 'message': '文件不存在'})
    
    if not os.path.exists(TEMP_FOLDER):
        os.makedirs(TEMP_FOLDER)
    
    unique_filename = get_unique_filename(TEMP_FOLDER, filename)
    dest_filepath = os.path.join(TEMP_FOLDER, unique_filename)
    
    os.rename(src_filepath, dest_filepath)
    return jsonify({'success': True, 'message': f'文件已重命名为 {unique_filename} 移动到 temp'})

@upload_bp.route('/xlsx/delete-batch', methods=['POST'])
@login_required
def delete_xlsx_files_batch():
    filenames = request.json.get('filenames', [])
    deleted = []
    for filename in filenames:
        src_filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(src_filepath):
            if not os.path.exists(TEMP_FOLDER):
                os.makedirs(TEMP_FOLDER)
            unique_filename = get_unique_filename(TEMP_FOLDER, filename)
            dest_filepath = os.path.join(TEMP_FOLDER, unique_filename)
            os.rename(src_filepath, dest_filepath)
            deleted.append(unique_filename)
    return jsonify({'success': True, 'deleted': deleted})

@upload_bp.route('/upload', methods=['POST'])
@login_required
def upload_files():
    if 'files[]' not in request.files:
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    files = request.files.getlist('files[]')
    uploaded = []
    skipped = []
    
    for file in files:
        if file.filename == '':
            continue
        if not file.filename.endswith(('.xlsx', '.xls')):
            continue
        
        filename = file.filename if file.filename.endswith('.xlsx') else file.filename + 'x'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        if os.path.exists(filepath):
            skipped.append(filename)
        else:
            file.save(filepath)
            uploaded.append(filename)
    
    return jsonify({
        'success': True,
        'uploaded': uploaded,
        'skipped': skipped,
        'message': f'上传成功: {len(uploaded)}个, 跳过: {len(skipped)}个'
    })

@upload_bp.route('/upload-config', methods=['POST'])
@login_required
def upload_config_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '文件名不能为空'})
    
    if not file.filename.endswith('.xlsx'):
        return jsonify({'success': False, 'message': '只能上传 .xlsx 文件'})
    
    filename = file.filename
    pattern = r'^config_\d{12}.*\.xlsx$'
    if not re.match(pattern, filename):
        return jsonify({'success': False, 'message': '文件名格式错误，必须为 config_年月日时分秒.xlsx (如 config_202603081033.xlsx)'})
    
    filepath = os.path.join(CONFIG_DIR, filename)
    
    if os.path.exists(filepath):
        return jsonify({'success': False, 'message': f'文件 {filename} 已存在，跳过上传'})
    
    file.save(filepath)
    return jsonify({'success': True, 'filename': filename})

@upload_bp.route('/config/list', methods=['GET'])
@login_required
def list_config_files():
    if not os.path.exists(CONFIG_DIR):
        return jsonify([])
    
    files = []
    for f in os.listdir(CONFIG_DIR):
        if f.endswith('.xlsx'):
            filepath = os.path.join(CONFIG_DIR, f)
            stat = os.stat(filepath)
            files.append({
                'name': f,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    return jsonify(files)

@upload_bp.route('/config/delete', methods=['POST'])
@login_required
def delete_config_file():
    if session.get('username') != 'admin':
        return jsonify({'success': False, 'message': '只有管理员可以删除配置文件'})
    
    filename = request.json.get('filename')
    if not filename:
        return jsonify({'success': False, 'message': '文件名不能为空'})
    
    filepath = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({'success': False, 'message': '文件不存在'})
    
    if not os.path.exists(TEMP_FOLDER):
        os.makedirs(TEMP_FOLDER)
    
    dest_filepath = os.path.join(TEMP_FOLDER, filename)
    if os.path.exists(dest_filepath):
        return jsonify({'success': False, 'message': 'temp目录已存在同名文件'})
    
    os.rename(filepath, dest_filepath)
    return jsonify({'success': True})

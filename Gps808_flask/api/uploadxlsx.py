from flask import Blueprint, request, jsonify, session, redirect
import os
from datetime import datetime

upload_bp = Blueprint('upload', __name__)

UPLOAD_FOLDER = 'excle'
TEMP_FOLDER = 'temp'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
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
    
    dest_filepath = os.path.join(TEMP_FOLDER, filename)
    if os.path.exists(dest_filepath):
        return jsonify({'success': False, 'message': 'temp目录已存在同名文件'})
    
    os.rename(src_filepath, dest_filepath)
    return jsonify({'success': True})

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
            dest_filepath = os.path.join(TEMP_FOLDER, filename)
            if not os.path.exists(dest_filepath):
                os.rename(src_filepath, dest_filepath)
                deleted.append(filename)
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

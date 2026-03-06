from flask import Flask, render_template, request, jsonify, session, redirect
import openpyxl
import os
import json
import sqlite3
from datetime import datetime, date, time
from functools import wraps

app = Flask(__name__)
app.secret_key = 'excel_editor_secret_key_2024'
EXCEL_FILE = 'config/config.xlsx'
UPLOAD_FOLDER = 'xlsx'
USERS_DB = 'config/user.db'

def get_db_connection():
    conn = sqlite3.connect(USERS_DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    cur = conn.execute('SELECT COUNT(*) FROM users')
    if cur.fetchone()[0] == 0:
        conn.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin123')")
        conn.commit()
    conn.close()

init_db()

def load_users():
    conn = get_db_connection()
    users = {row['username']: row['password'] for row in conn.execute('SELECT username, password FROM users')}
    conn.close()
    return users

def save_users(users):
    conn = get_db_connection()
    conn.execute('DELETE FROM users')
    for username, password in users.items():
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        if session.get('username') != 'admin':
            return '<script>alert("只有管理员可以访问");location.href="/"</script>'
        return f(*args, **kwargs)
    return decorated_function

def convert_value(val):
    if val is None:
        return ''
    if isinstance(val, (datetime, date, time)):
        return val.isoformat()
    return val

def get_workbook():
    if not os.path.exists(EXCEL_FILE):
        wb = openpyxl.Workbook()
        wb.remove(wb.active)
        wb.create_sheet('Sheet1')
        wb.save(EXCEL_FILE)
    return openpyxl.load_workbook(EXCEL_FILE)

def save_workbook(wb):
    wb.save(EXCEL_FILE)

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def login():
    username = request.json.get('username', '').strip()
    password = request.json.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    
    users = load_users()
    if username in users and users[username] == password:
        session['logged_in'] = True
        session['username'] = username
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': '用户名或密码错误'})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/check-admin', methods=['GET'])
@login_required
def check_admin():
    return jsonify({'isAdmin': session.get('username') == 'admin'})

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/xlsx')
@login_required
def xlsx_files():
    return render_template('xlsx.html')

@app.route('/admin')
@login_required
@admin_required
def admin_page():
    return render_template('admin.html')

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    users = load_users()
    return jsonify([{'username': k, 'password': v} for k, v in users.items()])

@app.route('/api/admin/user', methods=['POST'])
@admin_required
def add_user():
    username = request.json.get('username', '').strip()
    password = request.json.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    
    users = load_users()
    if username in users:
        return jsonify({'success': False, 'message': '用户已存在'})
    
    users[username] = password
    save_users(users)
    return jsonify({'success': True})

@app.route('/api/admin/user', methods=['PUT'])
@admin_required
def update_user():
    username = request.json.get('username', '').strip()
    password = request.json.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'})
    
    users = load_users()
    if username not in users:
        return jsonify({'success': False, 'message': '用户不存在'})
    
    users[username] = password
    save_users(users)
    return jsonify({'success': True})

@app.route('/api/admin/user', methods=['DELETE'])
@admin_required
def delete_user():
    username = request.json.get('username')
    if not username:
        return jsonify({'success': False, 'message': '用户名不能为空'})
    
    if username == 'admin':
        return jsonify({'success': False, 'message': '不能删除管理员'})
    
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': '用户不存在'})

@app.route('/api/data', methods=['GET'])
@login_required
def get_data():
    wb = get_workbook()
    ws = wb.active
    data = []
    for row in ws.iter_rows(values_only=True):
        row_data = [convert_value(cell) for cell in row]
        if any(cell != '' for cell in row_data):
            data.append(row_data)
    wb.close()
    response = jsonify(data)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/api/cell', methods=['POST'])
@login_required
def update_cell():
    wb = get_workbook()
    ws = wb.active
    row = int(request.json['row'])
    col = int(request.json['col'])
    value = request.json['value']
    ws.cell(row, col, value)
    save_workbook(wb)
    wb.close()
    return jsonify({'success': True})

@app.route('/api/cells', methods=['POST'])
@login_required
def update_cells():
    wb = get_workbook()
    ws = wb.active
    changes = request.json['changes']
    for item in changes:
        row = int(item['row'])
        col = int(item['col'])
        value = item['value']
        ws.cell(row, col, value)
    save_workbook(wb)
    wb.close()
    return jsonify({'success': True})

@app.route('/api/row', methods=['POST'])
@login_required
def add_row():
    wb = get_workbook()
    ws = wb.active
    count = int(request.json.get('count', 1))
    for _ in range(count):
        ws.append([''] * ws.max_column)
    save_workbook(wb)
    wb.close()
    return jsonify({'success': True})

@app.route('/api/row/<int:row_idx>', methods=['DELETE'])
@login_required
def delete_row(row_idx):
    wb = get_workbook()
    ws = wb.active
    ws.delete_rows(row_idx)
    save_workbook(wb)
    wb.close()
    return jsonify({'success': True})

@app.route('/api/xlsx/list', methods=['GET'])
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

@app.route('/api/xlsx/delete', methods=['POST'])
@login_required
def delete_xlsx_file():
    filename = request.json.get('filename')
    if not filename:
        return jsonify({'success': False, 'message': '文件名不能为空'})
    
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': '文件不存在'})

@app.route('/api/xlsx/delete-batch', methods=['POST'])
@login_required
def delete_xlsx_files_batch():
    filenames = request.json.get('filenames', [])
    deleted = []
    for filename in filenames:
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            deleted.append(filename)
    return jsonify({'success': True, 'deleted': deleted})

@app.route('/api/upload', methods=['POST'])
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

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True, port=5000)

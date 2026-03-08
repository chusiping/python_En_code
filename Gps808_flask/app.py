from flask import Flask, render_template, request, jsonify, session, redirect
import openpyxl
import os
import json
import sqlite3
from datetime import datetime, date, time
from functools import wraps
from api.config_edit import config_bp
from api.uploadxlsx import upload_bp
from api.exportjson import export_bp
from api.runtask import runtask_bp

app = Flask(__name__)
app.secret_key = 'excel_editor_secret_key_2024'
app.register_blueprint(config_bp, url_prefix='/api/config')
app.register_blueprint(upload_bp, url_prefix='/api')
app.register_blueprint(export_bp, url_prefix='/api')
app.register_blueprint(runtask_bp, url_prefix='/api')
EXCEL_FILE = 'config/config.xlsx'
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
            return redirect('/B6nM9qW2eR4tY7uI8oP0lK')
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/B6nM9qW2eR4tY7uI8oP0lK')
        if session.get('username') != 'admin':
            return '<script>alert("只有管理员可以访问");location.href="/"</script>'
        return f(*args, **kwargs)
    return decorated_function

@app.route('/B6nM9qW2eR4tY7uI8oP0lK')
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
    return jsonify({'isAdmin': session.get('username') == 'admin', 'username': session.get('username')})

@app.route('/')
def home():
    return '<h1>404 Not Found</h1>', 404

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/config')
@login_required
def config_edit():
    return render_template('config_edit.html')

@app.route('/xlsx')
@login_required
def xlsx_files():
    return render_template('uploadxlsx.html')

@app.route('/exportjson')
@login_required
def exportjson_page():
    return render_template('exportjson.html')

@app.route('/runtask')
@login_required
def runtask_page():
    return render_template('runtask.html')

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)

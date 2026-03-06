from flask import Blueprint, request, jsonify, session, redirect
import openpyxl
import os
from datetime import datetime, date, time

config_bp = Blueprint('config', __name__)

EXCEL_FILE = 'config/config.xlsx'

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
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

@config_bp.route('/data', methods=['GET'])
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

@config_bp.route('/cell', methods=['POST'])
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

@config_bp.route('/cells', methods=['POST'])
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

@config_bp.route('/row', methods=['POST'])
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

@config_bp.route('/row/<int:row_idx>', methods=['DELETE'])
@login_required
def delete_row(row_idx):
    wb = get_workbook()
    ws = wb.active
    ws.delete_rows(row_idx)
    save_workbook(wb)
    wb.close()
    return jsonify({'success': True})

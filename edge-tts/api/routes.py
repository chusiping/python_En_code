from flask import Blueprint, render_template, request, jsonify
import subprocess
import threading
import uuid
import os
import sys
import json
import asyncio
import edge_tts
from datetime import datetime

api_bp = Blueprint('api', __name__)

TASKS = {}
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
SAVE_DIR = os.path.join(BASE_DIR, 'download')
YT_DLP = os.path.join(BASE_DIR, 'yt-dlp', 'yt-dlp.exe')
PROXY = 'http://127.0.0.1:7890'
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SAVE_DIR, exist_ok=True)

DEFAULT_COOKIE_PATH = r'C:\Users\Administrator\Downloads\www.youtube.com_cookies.txt'


def get_cookie_path():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('cookie_path', DEFAULT_COOKIE_PATH)
    return DEFAULT_COOKIE_PATH


def save_cookie_path(path):
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
    config['cookie_path'] = path
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def run_task(task_id, task_type, url, quality=None):
    cmd = []
    if task_type == 'youtube_mp3':
        if not url:
            TASKS[task_id]['status'] = 'error'
            TASKS[task_id]['message'] = '请输入URL'
            return
        cookie_path = get_cookie_path()
        cmd = [
            YT_DLP,
            '--js-runtime', 'node',
            '--proxy', PROXY,
            '--cookies', cookie_path,
            '-x', '--audio-format', 'mp3',
            url,
            '-o', os.path.join(SAVE_DIR, '%(title)s.%(ext)s').replace('\\', '\\\\'),
            '--extractor-args', 'youtube:player_client=default,-android_sdkless'
        ]
    elif task_type == 'youtube_mp4':
        if not url:
            TASKS[task_id]['status'] = 'error'
            TASKS[task_id]['message'] = '请输入URL'
            return
        cookie_path = get_cookie_path()
        res = '720' if quality == '720' else '1080'
        cmd = [
            YT_DLP,
            '--js-runtime', 'node',
            '--proxy', PROXY,
            '--cookies', cookie_path,
            '-S', f'vcodec:h264,res:{res},acodec:aac',
            url,
            '-o', os.path.join(SAVE_DIR, '%(title)s.%(ext)s').replace('\\', '\\\\'),
            '--extractor-args', 'youtube:player_client=default,-android_sdkless'
        ]
    elif task_type == 'youtube_upgrade':
        cmd = [YT_DLP, '-U', '--proxy', PROXY]
    elif task_type == 'to_mp3':
        if not url:
            TASKS[task_id]['status'] = 'error'
            TASKS[task_id]['message'] = '请输入文件地址'
            return
        input_file = url.strip().strip('"').strip("'")
        if not os.path.exists(input_file):
            TASKS[task_id]['status'] = 'error'
            TASKS[task_id]['message'] = '文件不存在'
            return
        file_dir = os.path.dirname(input_file)
        file_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = os.path.join(file_dir, file_name + '.mp3')
        cmd = ['ffmpeg.exe', '-i', input_file, '-vn', output_file]
    
    TASKS[task_id]['status'] = 'running'
    TASKS[task_id]['message'] = '正在执行...'
    TASKS[task_id]['logs'] = []
    TASKS[task_id]['error_msg'] = ''

    log_file = os.path.join(LOG_DIR, f'{task_id}.log')
    TASKS[task_id]['log_file'] = log_file

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, shell=True, encoding='utf-8', errors='replace')
        TASKS[task_id]['process'] = proc
        TASKS[task_id]['pid'] = proc.pid

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f'命令: {" ".join(cmd)}\n')
            f.write(f'YT_DLP: {YT_DLP}\n')
            f.write(f'SAVE_DIR: {SAVE_DIR}\n')
            f.write(f'Cookie: {get_cookie_path()}\n')
            f.write(f'开始时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write('-' * 50 + '\n')

            for line in iter(lambda: proc.stdout.readline(), ''):
                if line:
                    line = line.strip()
                    TASKS[task_id]['logs'].append(line)
                    TASKS[task_id]['last_update'] = line
                    f.write(line + '\n')
                    f.flush()

            f.write('-' * 50 + '\n')
            f.write(f'结束时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')

        proc.stdout.close()
        proc.wait()
        logs = TASKS[task_id].get('logs', [])
        has_error = any('ERROR' in line.upper() or 'error' in line.lower() for line in logs)
        if has_error or proc.returncode not in [0, 1]:
            TASKS[task_id]['status'] = 'error'
            TASKS[task_id]['message'] = f'下载失败，返回码: {proc.returncode}'
            TASKS[task_id]['error_msg'] = f'返回码: {proc.returncode}'
        else:
            TASKS[task_id]['status'] = 'completed'
            TASKS[task_id]['message'] = '下载完成'
            TASKS[task_id]['message'] = '完成'
    except Exception as e:
        TASKS[task_id]['status'] = 'error'
        TASKS[task_id]['message'] = str(e)
        TASKS[task_id]['error_msg'] = str(e)
        TASKS[task_id]['logs'].append(f'错误: {str(e)}')
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f'错误: {str(e)}\n')


@api_bp.route('/run', methods=['POST'])
def run():
    data = request.json
    task_type = data.get('type')
    url = data.get('url', '').strip()
    quality = data.get('quality', '720').strip()

    task_id = str(uuid.uuid4())[:8]
    TASKS[task_id] = {
        'type': task_type,
        'url': url,
        'quality': quality,
        'status': 'pending',
        'message': '等待执行...',
        'pid': None,
        'process': None,
        'last_update': None
    }

    thread = threading.Thread(target=run_task, args=(task_id, task_type, url, quality))
    thread.daemon = True
    thread.start()

    return jsonify({'task_id': task_id, 'status': 'started'})


@api_bp.route('/status/<task_id>')
def status(task_id):
    task = TASKS.get(task_id)
    if not task:
        return jsonify({'error': '任务不存在'}), 404

    return jsonify({
        'task_id': task_id,
        'type': task.get('type'),
        'url': task.get('url'),
        'quality': task.get('quality'),
        'status': task['status'],
        'message': task['message'],
        'pid': task.get('pid'),
        'last_update': task.get('last_update')
    })


@api_bp.route('/tasks')
def tasks():
    return jsonify([
        {
            'task_id': tid,
            'type': t.get('type'),
            'url': t.get('url'),
            'quality': t.get('quality'),
            'status': t['status'],
            'message': t['message'],
            'error_msg': t.get('error_msg', ''),
            'logs': t.get('logs', []),
            'pid': t.get('pid'),
            'last_update': t.get('last_update')
        }
        for tid, t in TASKS.items()
    ])


@api_bp.route('/cookie', methods=['GET', 'POST'])
def cookie():
    if request.method == 'POST':
        data = request.json
        cookie_path = data.get('cookie_path', '').strip()
        if cookie_path:
            save_cookie_path(cookie_path)
        return jsonify({'success': True})
    return jsonify({'cookie_path': get_cookie_path()})


@api_bp.route('/kill/<task_id>', methods=['POST'])
def kill(task_id):
    task = TASKS.get(task_id)
    if not task:
        return jsonify({'error': '任务不存在'}), 404
    
    proc = task.get('process')
    if proc:
        try:
            proc.terminate()
        except:
            pass
    
    del TASKS[task_id]
    return jsonify({'success': True})


async def generate_tts_audio(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


@api_bp.route('/tts', methods=['POST'])
def tts():
    data = request.json
    text = data.get('text', '').strip()
    voice = data.get('voice', 'zh-CN-XiaoxiaoNeural')
    
    if not text:
        return jsonify({'success': False, 'error': '请输入文字'}), 400
    
    task_id = str(uuid.uuid4())[:8]
    output_file = os.path.join(SAVE_DIR, f'{task_id}.mp3')
    
    TASKS[task_id] = {
        'type': 'tts',
        'text': text,
        'voice': voice,
        'status': 'running',
        'message': '正在生成音频...',
        'output_file': output_file,
        'pid': None,
        'process': None,
        'last_update': None
    }
    
    def run_tts():
        try:
            asyncio.run(generate_tts_audio(text, voice, output_file))
            TASKS[task_id]['status'] = 'completed'
            TASKS[task_id]['message'] = '生成完成'
        except Exception as e:
            TASKS[task_id]['status'] = 'error'
            TASKS[task_id]['message'] = str(e)
            TASKS[task_id]['error_msg'] = str(e)
    
    thread = threading.Thread(target=run_tts)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'task_id': task_id, 'output_file': output_file})

from flask import Blueprint, request, jsonify
import uuid
import os
import asyncio
import edge_tts


api_bp = Blueprint('api', __name__)

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
os.makedirs(SAVE_DIR, exist_ok=True)


async def generate_tts_audio(text, voice, output_path):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


@api_bp.route('/tts', methods=['POST'])
def tts():
    data = request.json
    text = data.get('text', '').strip()
    voice = data.get('voice', 'zh-CN-XiaoxiaoNeural')
    topic = data.get('topic', '').strip()
    
    if not topic:
        topic = 'temp'
    
    base_filename = f"{topic}.mp3"
    output_file = os.path.join(SAVE_DIR, base_filename)
    
    if os.path.exists(output_file):
        i = 1
        while os.path.exists(os.path.join(SAVE_DIR, f"{topic}_{i}.mp3")):
            i += 1
        output_file = os.path.join(SAVE_DIR, f"{topic}_{i}.mp3")
    
    try:
        asyncio.run(generate_tts_audio(text, voice, output_file))
        return jsonify({'success': True, 'output_file': output_file})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/files', methods=['GET'])
def list_files():
    files = []
    for f in os.listdir(SAVE_DIR):
        if f.endswith('.mp3'):
            files.append({
                'name': f,
                'path': f'/output/{f}'
            })
    return jsonify(files)


@api_bp.route('/files/delete', methods=['POST'])
def delete_files():
    data = request.json
    files = data.get('files', [])
    
    errors = []
    for filename in files:
        filepath = os.path.join(SAVE_DIR, filename)
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")
    
    if errors:
        return jsonify({'success': False, 'error': '; '.join(errors)}), 500
    return jsonify({'success': True})

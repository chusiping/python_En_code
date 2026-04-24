from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, template_folder='template')

from api import routes
app.register_blueprint(routes.api_bp, url_prefix='/api')

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('xiazai.html')

@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

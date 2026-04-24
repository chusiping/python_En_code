from flask import Flask, render_template

app = Flask(__name__, template_folder='template')

from api import routes
app.register_blueprint(routes.api_bp, url_prefix='/api')

@app.route('/')
def index():
    return render_template('xiazai.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

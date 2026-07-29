from flask import Flask, jsonify, render_template_string
import os
import json
app = Flask(__name__)
RESULT_DIR = "result"
# 首页：列出所有json
@app.route("/")
def index():
    files = []
    for f in os.listdir(RESULT_DIR):
        if f.endswith(".json"):

                path = os.path.join(
                    RESULT_DIR,
                    f
                )

                files.append(
                    (
                        f,
                        os.path.getmtime(path)
                    )
                )
    # 按修改时间倒序
    files.sort(
        key=lambda x: x[1],
        reverse=True
    )
    # 只取最新200个
    files = [
        x[0]
        for x in files[:10]
]
    files.sort(reverse=True)
    html = """
    <h2>解析结果列表</h2>
    <ul>
    {% for f in files %}
        <li>
            <a href="/view/{{f}}">
                {{f}}
            </a>
        </li>
    {% endfor %}
    </ul>
    """
    return render_template_string(
        html,
        files=files
    )
# 查看单个json
@app.route("/view/<filename>")
def view(filename):
    path = os.path.join(
        RESULT_DIR,
        filename
    )
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        data=json.load(f)
    html="""
    <h2>{{filename}}</h2>
    <pre>
{{data}}
    </pre>
    <a href="/">返回</a>
    """
    return render_template_string(
        html,
        filename=filename,
        data=json.dumps(
            data,
            ensure_ascii=False,
            indent=4
        )
    )
if __name__=="__main__":
    app.run(
        host="0.0.0.0",
        port=7534,
        debug=True
    )
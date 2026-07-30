from flask import request, Flask, render_template, render_template_string
import json
import os

app = Flask(__name__)
RESULT_DIR = "result"
# ===============================
# JSON展开
# ===============================
def flatten_json(data, parent=""):
    result = []
    if isinstance(data, dict):
        for key, value in data.items():
            name = f"{parent}.{key}" if parent else key
            if isinstance(value, (dict, list)):
                result.extend(
                    flatten_json(
                        value,
                        name
                    )
                )
            else:
                result.append(
                    (
                        name,
                        value
                    )
                )
    elif isinstance(data, list):
        for i, value in enumerate(data):
            name = f"{parent}[{i}]"
            if isinstance(value, (dict, list)):
                result.extend(
                    flatten_json(
                        value,
                        name
                    )
                )
            else:
                result.append(
                    (
                        name,
                        value
                    )
                )
    else:
        result.append(
            (
                parent,
                data
            )
        )
    return result
# ===============================
# 首页
# ===============================
@app.route("/")
def index():
    # 默认显示50条
    limit = request.args.get(
        "limit",
        default=30,
        type=int
    )
    files = []
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)
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
    # 最新在前
    files.sort(
        key=lambda x: x[1],
        reverse=True
    )
    files = [
        x[0]
        for x in files[:limit]
    ]
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>JT808解析结果</title>
    </head>
    <body>
    <h2>JT808解析结果</h2>
    <ul>
    {% for f in files %}
        <li>
            <a href="/view/{{f}}" target="_blank">
                {{f}}
            </a>
        </li>
    {% endfor %}
    </ul>
    </body>
    </html>
    """
    return render_template_string(
        html,
        files=files
    )
# ===============================
# 查看JSON
# ===============================
@app.route("/view/<filename>")
def view(filename):
    path = os.path.join(
        RESULT_DIR,
        filename
    )
    if not os.path.exists(path):
        return "文件不存在"
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)
    table_data = flatten_json(data)
    return render_template(
        "table.html",
        filename=filename,
        data=table_data
    )
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=7535,
        debug=True
    )
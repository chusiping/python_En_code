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
                result.extend(flatten_json(value, name))
            else:
                result.append((name, value))
    elif isinstance(data, list):
        for i, value in enumerate(data):
            name = f"{parent}[{i}]"
            if isinstance(value, (dict, list)):
                result.extend(flatten_json(value, name))
            else:
                result.append((name, value))
    else:
        result.append((parent, data))
    return result

# ===============================
# 首页（支持递归查找多级子目录）
# ===============================
@app.route("/")
def index():
    limit = request.args.get("limit", default=100, type=int)
    files = []
    
    if not os.path.exists(RESULT_DIR):
        os.makedirs(RESULT_DIR)
        
    # 使用 os.walk 递归遍历 result 文件夹下的所有子目录
    for root, dirs, filenames in os.walk(RESULT_DIR):
        for f in filenames:
            if f.endswith(".json"):
                # 获取文件的完整绝对/相对路径
                full_path = os.path.join(root, f)
                # 计算出相对于 RESULT_DIR 的相对路径（例如: 202608/080918/test.json）
                rel_path = os.path.relpath(full_path, RESULT_DIR)
                
                files.append((
                    rel_path, 
                    os.path.getmtime(full_path)
                ))
                
    # 最新在前
    files.sort(key=lambda x: x[1], reverse=True)
    files = [x[0] for x in files[:limit]]
    
    # 注意：前端 a 标签的 href 路径改成了 /view/{{f}}，Jinja2 会自动转义斜杠
    html = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>JT808解析结果</title>
    </head>
    <body>
    <h2>JT808解析结果</h2>
    <ol>
    {% for f in files %}
        <li>
            <a href="/view/{{ f }}" target="_blank">
                {{ f }}
            </a>
        </li>
    {% endfor %}
    </ol>
    </body>
    </html>
    """
    return render_template_string(html, files=files)

# ===============================
# 查看JSON（使用 path 转换器支持子路径）
# ===============================
@app.route("/view/<path:filename>")
def view(filename):
    # Flask 的 path 转换器允许 filename 包含斜杠（例如 202608/080918/xxx.json）
    path = os.path.join(RESULT_DIR, filename)
    
    if not os.path.exists(path):
        return "文件不存在"
        
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    table_data = flatten_json(data)
    return render_template("table.html", filename=filename, data=table_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7535, debug=True)

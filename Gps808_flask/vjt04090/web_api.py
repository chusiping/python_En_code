from flask import Flask, render_template
import json
import os
from web_json import *

app = Flask(__name__)
@app.route("/")
def index():

    with open(
        "result/0200_位置信息_1.json",
        encoding="utf-8"
    ) as f:

        data=json.load(f)


    table_data = flatten_json(data)


    return render_template(
        "table.html",
        data=table_data
    )

if __name__=="__main__":

    app.run(
        host="0.0.0.0",
        port=8080
    )
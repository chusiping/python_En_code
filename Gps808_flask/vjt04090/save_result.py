import json
import os
from datetime import datetime
counter = 0
def save_result(result):
    global counter
    counter += 1
    # 创建目录
    os.makedirs(
        "./Gps808_flask/result",
        exist_ok=True
    )
    # 文件名
    filename = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
    filename += f"_{counter:06d}.json"
    filepath = os.path.join(
        "result",
        filename
    )
    data = {
        "time": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "data": result
    }
    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )
    return filepath
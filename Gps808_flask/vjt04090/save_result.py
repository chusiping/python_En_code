import json
import os
from datetime import datetime
counter = 0

def find_value(data, key):
    if isinstance(data, dict):
        if key in data:
            return data[key]
        for v in data.values():
            r = find_value(v, key)
            if r is not None:
                return r
    elif isinstance(data, list):
        for item in data:
            r = find_value(item, key)
            if r is not None:
                return r
    return None

def save_result(result):
    global counter
    counter += 1
    # 创建目录
    os.makedirs(
        "result",
        exist_ok=True
    )

    # 文件名
    # 获取手机号和消息ID，没有则使用unknown
    phone = str(
        find_value(result, "终端号")
        or find_value(result, "终端手机号")
        or find_value(result, "手机号")
        or "unknown"
    )

    msg_id = str(
        find_value(result, "消息ID")
        or find_value(result, "信息ID")
        or "unknown"
    ).replace("[", "").replace("]", "")


    # 去掉消息ID里的[]（如果有）
    msg_id = msg_id.replace("[", "").replace("]", "")

    # 平台通用应答(8001)不保存
    if msg_id == "8001":
        print("8001应答不记录json文件")
        return None

    # 生成文件名：手机号_消息ID_年月日时分秒_序号.json
    filename = (
        f"{phone}_{msg_id}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
        f"{counter:06d}.json"
    )

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
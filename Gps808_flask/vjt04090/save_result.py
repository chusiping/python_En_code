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

def check_condition(d):
    """递归检查字典中是否包含指定的键值对规则"""
    if not isinstance(d, dict):
        return False
    # 定义目标规则：值为空则只检查键是否存在；值不为空则需要 name 包含该字符串
    target_rules = {
        "5224": "环卫车工况",
        "5223": ""
    }
    
    # 1. 检查当前层级的键
    for key, item in d.items():
        str_key = str(key)
        if str_key in target_rules:
            target_val = target_rules[str_key]
            # 规则1：配置的值为空，只要键存在就直接返回 True
            if not target_val:
                return True
            # 规则2：配置的值不为空，需要 item 是字典，且 item["name"] 包含该值
            if isinstance(item, dict) and "name" in item and target_val in str(item["name"]):
                return True
                
    # 2. 如果当前层的所有键都不满足条件，再继续向子层级深挖递归
    for value in d.values():
        if isinstance(value, dict):
            if check_condition(value):
                return True
        elif isinstance(value, list):
            for sub_item in value:
                if isinstance(sub_item, dict) and check_condition(sub_item):
                    return True
    return False


def save_result(result):
    # 使用递归函数进行深度过滤
    if not check_condition(result):
        print("未包含5224 ， 5223环卫车工况相关数据，跳过保存。")
        return None

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
    if msg_id in ["8001", "0900"]:
        print(f"{msg_id}应答不记录json文件") 
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

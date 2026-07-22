import json
import os

def load_protocol_config(config_dir="config"):
    protocol_map = {}
    if not os.path.exists(config_dir):
        raise Exception(
            f"配置目录不存在: {config_dir}"
        )
    for file in os.listdir(config_dir):
        if not file.endswith(".json"):
            continue
        path = os.path.join(
            config_dir,
            file
        )
        try:
            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:
                config = json.load(f)
            protocol = config.get(
                "protocol"
            )
            messages = config.get(
                "messages",
                []
            )
            if not protocol:
                continue
            # 转集合，提高查询速度
            protocol_map[protocol] = set(
                messages
            )
            print(
                f"加载协议: {protocol}, "
                f"消息数量:{len(messages)}"
            )
        except Exception as e:
            print(
                f"加载失败 {file}: {e}"
            )
    return protocol_map
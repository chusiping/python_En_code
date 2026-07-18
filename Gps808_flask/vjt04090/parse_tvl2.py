from codec import *
# 通用 TLV 核心解析器
def parse_tlv(data, id_bytes, parser_map=None):
    """参数解释 data:十六进制字符串    id_bytes:ID占几个字节(JT808附加信息:1  EA/EE内部:2)  parser_map:当前层ID对应解析函数"""
    result = {}
    idx = 0
    while idx < len(data):
        # =================
        # ID
        # =================
        id_len = id_bytes * 2

        if idx + id_len > len(data):
            break
        item_id = data[idx:idx+id_len]
        idx += id_len
        # =================
        # 长度
        # =================
        if idx + 2 > len(data):
            break
        length = int(
            data[idx:idx+2],
            16
        )
        idx += 2
        # =================
        # 数据
        # =================
        value_len = length * 2
        value = data[
            idx:
            idx + value_len
        ]
        idx += value_len
        # =================
        # 查找解析器
        # =================
        info = None
        if parser_map:
            info = parser_map.get(item_id) # 得到 id , nanme , parse函数
        # =================
        # 未定义
        # =================
        if info is None:
            result[item_id] = {
                "名称":"未知",
                "长度":length,
                "数据":value
            }
            continue
        name = info.get(
            "name",
            "未知"
        )
        parser = info.get(
            "parser"
        )
        children = info.get(
            "children"
        )
        # =================
        # 第一种:
        # 函数解析
        # =================
        if parser:
            parsed_data = parser(value)
        # =================
        # 第二种:
        # 子TLV递归
        # ================
        elif children:
            parsed_data = parse_tlv(
                value,
                children["id_bytes"],
                children["map"]
            )
        # =================
        # 第三种:
        # 原始数据
        # =================
        else:
            parsed_data = value
        result[item_id] = {
            "名称":name,
            "长度":length,
            "数据":parsed_data
        }
    return result
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

"""
函数解释：
1 这个设计的核心就是：通过映射表描述协议结构，然后根据映射表一层一层往下解析
2 第一层映射 att_info = parse_tlv(tlv_data,1,Map_E1_to_EE) 
  遇到 EA：不要直接解析数据。进入下一层
    Map_E1_to_EE = {
        "EA": {
            "name": "基础数据流",
            "children":{
                "id_bytes":2,
                "map":EA_解析EA下的所有ID
            }
    }
    

3   第二层：EA内部数据项 遇到：0003不要直接解析。继续往下

    EA_解析EA下的所有ID = {
    "0001":{ "name":"预留", "parser":None },
    "0002":{ "name":"预留", "parser":None },
    "0003":{
        "name":"总里程",
        "children":{
            "id_bytes":1,
            "map":MILEAGE_MAP
        }
    }

4   这次有 parser 开始解析
    MILEAGE_MAP={
        "01":{
            "name":"GPS总里程",
            "parser":parse_ea_0003
        },
        "02":{
            "name":"J1939里程",
            "parser":parse_ea_0003
        }
    }
        
5 节序序列 1 长度 4 就是 0100001234 这种 10长度的
  字节序列 0 长度 1 就是 0B 

  01   00   00   12   34  序列0长度1  从位置0开始 取1个字节 01
  01   00   00   12   34  序列1长度14 从位置1开始 取4个字节 00   00   12   34

"""
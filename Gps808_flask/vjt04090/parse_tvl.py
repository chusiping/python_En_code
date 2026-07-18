from codec import *
from PARSER_E1_to_EE import * 
# 通用 TLV 核心解析器
def parse_tlv_func(data, id_bytes, parser_map=None):
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
        if info:
            parsed_data = info["parser"](value)
            name = info["name"]
        else:
            parsed_data = value
            name = "未知"
        result[item_id] = {
            "名称": name,
            "长度": length,
            "数据": parsed_data
        }
    return result


EA_MAP = {
    "0001":{ "name":"预留", "parser":None },
    "0002":{ "name":"预留", "parser":None },
    "0003":{ "name":"总里程数据", "parser":parse_ea_0003 },
    "0004":{ "name":"总油耗/总电耗", "parser":parse_tlv_func },
    "0005":{ "name":"总运行时长", "parser":parse_tlv_func },
    "0006":{ "name":"总熄火时长", "parser":parse_tlv_func },
    "0007":{ "name":"总怠速时长", "parser":parse_tlv_func },

    "0010":{ "name":"加速度表", "parser":parse_tlv_func },
    "0011":{ "name":"车辆状态表", "parser":parse_tlv_func },
    "0012":{ "name":"车辆电压", "parser":parse_tlv_func },
    "0013":{ "name":"终端内置电池电压", "parser":parse_tlv_func },
    "0014":{ "name":"CSQ值", "parser":parse_tlv_func },
    "0015":{ "name":"车型ID", "parser":parse_tlv_func },
    "0016":{ "name":"OBD协议类型", "parser":parse_tlv_func },
    "0017":{ "name":"驾驶循环标签", "parser":parse_tlv_func },
    "0018":{ "name":"GPS收星数", "parser":parse_tlv_func },
    "0019":{ "name":"GPS位置精度", "parser":parse_tlv_func },
    "001A":{ "name":"GPS平均信噪比", "parser":parse_tlv_func },
    "001B":{ "name":"GPS天线状态", "parser":parse_tlv_func },
    "001D":{ "name":"设备拔出状态", "parser":parse_tlv_func },
    "001E":{ "name":"累计里程", "parser":parse_tlv_func },

    "0020":{ "name":"点火类型", "parser":parse_tlv_func },
    "0021":{ "name":"碳排放量", "parser":parse_tlv_func },
    "0022":{ "name":"Roll角速度", "parser":parse_tlv_func },
    "0023":{ "name":"Pitch角速度", "parser":parse_tlv_func },
    "0024":{ "name":"Yaw角速度", "parser":parse_tlv_func },
    "0025":{ "name":"累计里程2", "parser":parse_tlv_func },
    "0026":{ "name":"输入状态", "parser":parse_tlv_func },
    "0027":{ "name":"GPS定位解状态", "parser":parse_tlv_func },
    "0028":{ "name":"设备运行时间", "parser":parse_tlv_func },
    "0029":{ "name":"空调状态表", "parser":parse_tlv_func }

}

# 4.32   附表 位置数据信息体 --->  4.35   附表 位置附加信息表 ---> 4.36   附表 附加信息定义 ---> 0xEA T808标准附加信息ID  ---> 4.37  附表 基础数据流




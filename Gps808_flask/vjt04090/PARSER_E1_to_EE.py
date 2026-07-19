from codec import *

# 4.45   附表_基础数据项：总里程格式表 
def parse_ea_0003(data):
    if len(data) < 10:
        return {
            "错误": "总里程数据长度不足"
        }
    mileage_type = data[0:2]
    mileage_hex = data[2:10]
    mileage = int(mileage_hex, 16)

    type_map = {
        "01": "GPS总里程(累计)",
        "02": "J1939里程算法1",
        "03": "J1939里程算法2",
        "04": "J1939里程算法3",
        "05": "J1939里程算法4",
        "06": "J1939里程算法5",
        "07": "OBD仪表里程",
        "08": "OBD速度里程",
        "09": "J1939里程算法6",
        "0A": "J1939里程算法7",
        "0B": "J1939里程算法8",
        "0C": "J1939里程算法9"
    }
    return {
        "里程类型": mileage_type,
        "类型说明": type_map.get(
            mileage_type,
            "未知类型"
        ),
        "总里程": mileage,
        "原始数据":data,
        "单位": "米"
    }

# 4.45   附表_基础数据项：总耗油/总电耗量格式表
def parse_ea_0004(data):
    if len(data) < 10:
        return {
            "错误": "总耗油数据长度不足",
            "数据": data
        }
    consume_type = data[0:2]
    value_hex = data[2:10]
    type_map = {
        "01":"J1939油耗算法1",
        "02":"J1939油耗算法2",
        "03":"J1939油耗算法3",
        "04":"J1939油耗算法4",
        "05":"J1939油耗算法5",
        "0B":"OBD油耗算法1",
        "0C":"OBD油耗算法2",
        "0D":"OBD油耗算法3",
        "0E":"OBD油耗算法4",
        "10":"OBD油耗算法5",
        "A0":"电耗算法1"
    }
    value = int(
        value_hex,
        16
    )
    result = {
        "类型":
            type_map.get(
                consume_type,
                "4.47 附表_基础数据项(附表查询无此类型)"
            ),
        "原始值":
            data
    }
    # 电耗
    if consume_type == "A0":
        result["电耗"] = value / 100
        result["单位"] = "KWH"
    else:
        result["油耗"] = value
        result["单位"] = "ML"
    return result

# 4.45   附表_基础数据项：加速度表
"""举例  0004  00FA      0010 0020 0030 0040   0100
        点数4  间隔250ms                       最大值
"""
def parse_ea_0010(data):
    result = {}
    # 至少:
    # 点数量2字节
    # 间隔2字节
    # 最大值2字节
    if len(data) < 12:
        return {
            "错误": "加速度数据长度不足",
            "数据": data
        }
    # ----------------
    # 采集点数量
    # ----------------
    point_count = int(
        data[0:4],
        16
    )
    # ----------------
    # 采集间隔
    # ----------------
    interval = int(
        data[4:8],
        16
    )
    result["采集点数量"] = point_count
    result["采集间隔"] = interval
    result["单位"] = "ms"
    # ----------------
    # 加速度点
    # ----------------
    points = []
    index = 8
    for i in range(point_count):
        if index + 4 > len(data):
            break
        value = int(
            data[index:index+4],
            16
        )
        points.append({
            "序号": i+1,
            "加速度": value,
            "单位": "mg"
        })
        index += 4
    result["采集点"] = points
    # ----------------
    # 最大加速度
    # ----------------
    if index + 4 <= len(data):
        max_value = int(
            data[index:index+4],
            16
        )
        result["最大加速度"] = {
            "值": max_value,
            "单位": "mg"
        }
    return result

# 4.50   附表_基础数据项：车辆状态表
def parse_ea_0011(data):
    if len(data) < 22:
        return {
            "错误": "车辆状态数据长度不足",
            "数据": data
        }
    # 转byte数组
    bytes_data = bytes.fromhex(data)
    result = {}
    # ======================
    # 字节0 状态掩码
    # ======================
    result["状态掩码"] = {
        "原始值": bytes_data[0]
    }
    # ======================
    # 字节1 安全状态
    # ======================
    b = bytes_data[1]
    result["安全状态"] = {
        "ACC状态":
            "ON" if b & 0x01 else "OFF",
        "设防状态":
            "设防" if b & 0x02 else "撤防",
        "脚刹":
            "踩下" if b & 0x04 else "松开",
        "油门":
            "踩下" if b & 0x08 else "松开",
        "手刹":
            "拉起" if b & 0x10 else "放下",
        "主安全带":
            "插入" if b & 0x20 else "松开",
        "副安全带":
            "插入" if b & 0x40 else "松开",
        "发动机":
            "ON" if b & 0x80 else "OFF"
    }
    # ======================
    # 字节2 门状态
    # ======================
    b = bytes_data[2]
    result["门状态"] = {
        "左前门":
            "开" if b & 0x01 else "关",
        "右前门":
            "开" if b & 0x02 else "关",
        "左后门":
            "开" if b & 0x04 else "关",
        "右后门":
            "开" if b & 0x08 else "关",
        "后备箱":
            "开" if b & 0x10 else "关",
        "发动机盖":
            "开" if b & 0x20 else "关"
    }
    # ======================
    # 字节3 锁状态
    # ======================

    b =bytes_data[3]

    result["锁状态"] = {
        "左前锁":
            "落锁" if b & 0x01 else "开锁",
        "右前锁":
            "落锁" if b & 0x02 else "开锁",
        "左后锁":
            "落锁" if b & 0x04 else "开锁",
        "右后锁":
            "落锁" if b & 0x08 else "开锁"
    }
    # ======================
    # 字节4 窗户状态
    # ======================
    b = bytes_data[4]
    result["窗户状态"] = {
        "左前窗":"开" if b&0x01 else "关",
        "右前窗":"开" if b&0x02 else "关",
        "左后窗":"开" if b&0x04 else "关",
        "右后窗":"开" if b&0x08 else "关",
        "天窗":"开" if b&0x10 else "关",
        "左转向灯":"开" if b&0x20 else "关",
        "右转向灯":"开" if b&0x40 else "关",
        "阅读灯":"开" if b&0x80 else "关"
    }
    # ======================
    # 字节5 灯光状态
    # ======================
    b = bytes_data[5]
    result["灯光状态"] = {
        "近光灯":"开" if b&0x01 else "关",
        "远光灯":"开" if b&0x02 else "关",
        "前雾灯":"开" if b&0x04 else "关",
        "后雾灯":"开" if b&0x08 else "关",
        "危险灯":"开" if b&0x10 else "关",
        "倒车灯":"开" if b&0x20 else "关",
        "AUTO灯":"开" if b&0x40 else "关",
        "示宽灯":"开" if b&0x80 else "关"
    }
    # ======================
    # 字节6 开关状态A
    # ======================
    b = bytes_data[6]
    result["开关状态A"]={
        "机油报警":
            "ON" if b&0x01 else "OFF",
        "燃油报警":
            "ON" if b&0x02 else "OFF",
        "雨刷":
            "开" if b&0x04 else "关",
        "喇叭":
            "开" if b&0x08 else "关",
        "空调":
            "开" if b&0x10 else "关",
        "后视镜":
            "开" if b&0x20 else "关"
    }
    # ======================
    # 字节7 档位
    # ======================

    gear = bytes_data[7] & 0x0F
    gear_map = {
        0:"P",
        1:"R",
        2:"N",
        3:"D",
        4:"1",
        5:"2",
        6:"3",
        7:"4",
        8:"5",
        9:"6",
        10:"M",
        11:"S",
        12:"B",
        13:"L",
        15:"不存在"
    }
    result["档位"] = gear_map.get(
        gear,
        "未知"
    )
    # ======================
    # 字节8 钥匙状态
    # ======================
    b = bytes_data[8]
    result["钥匙状态"]={
        "供电状态":
            "供电" if b&0x01 else "断电",
        "钥匙":
            "存在" if b&0x02 else "不存在"
    }
    return result

# 4.49   附表_基础数据项：协议类型表
def parse_ea_0016(data):
    protocol_map = {
        "11": "CAN 11_500",
        "12": "CAN 11_250",
        "13": "CAN 29_500_EX",
        "14": "CAN 29_250_EX",
        "20": "KWP2000",
        "30": "KWP2000M",
        "40": "ISO9141",
        "50": "VPW",
        "60": "PWM",
        "70": "PRIVATE",
        "F0": "J1939"
    }
    if len(data) < 2:
        return {
            "错误": "协议类型数据长度不足",
            "数据": data
        }
    value = data[:2].upper()
    return {
        "协议类型编码": "0x" + value,
        "协议类型": protocol_map.get(
            value,
            "未知协议"
        )
    }

def parse_ea_001B(data):
    status_map = {
        "00": "天线正常",
        "01": "天线开路",
        "02": "天线短路"
    }
    if len(data) < 2:
        return {
            "错误": "GPS天线状态数据长度不足",
            "数据": data
        }
    value = data[:2].upper()
    return {
        "状态编码": "0x" + value,
        "GPS天线状态": status_map.get(
            value,
            "未知状态"
        )
    }

def parse_ea_001D(data):
    if len(data) < 2:
        return {
            "错误": "设备拔出状态数据长度不足",
            "数据": data
        }
    value = data[:2].upper()
    if value == "02":
        status = "设备拔出 或者 设备上电后第一次定位前"
    else:
        status = "其他"
    return {
        "状态编码": "0x" + value,
        "设备状态": status
    }

def parse_3001(value):  #   3001 正反转
    status = int(value,16)
    return {
        0:"停转",
        1:"正转",
        2:"反转"
    }.get(status,"未知")
def parse_3002(value):  #   3002~3005 温度
    temp = int(value,16)
    return temp / 10 - 40
def parse_300D(value):
    if len(value)==4:
        temp=int(value,16)/10-40
        return {
            "温度":temp
        }
    elif len(value)==16:
        temp=int(value[0:4],16)/10-40
        hum=int(value[4:8],16)/10
        volt=int(value[8:12],16)/100
        tamper=value[12:14]
        signal=int(value[14:16],16)
        if signal>=128:
            signal-=256
        return {
            "温度":temp,
            "湿度":hum,
            "电压":volt,
            "拆卸":"未拆卸" if tamper=="FF" else "已拆卸",
            "信号":signal
        }
    return value
def parse_3013(value):
    return {
        "Total":parse_3013_s16(value[0:4]),
        "X":parse_3013_s16(value[4:8]),
        "Y":parse_3013_s16(value[8:12]),
        "Z":parse_3013_s16(value[12:16])
    }
def parse_3013_s16(hexstr):
    value=int(hexstr,16)
    if value>=0x8000:
        value-=0x10000
    return value
# 0x3014  输入和输出状态  8字节
def parse_3014(value):
    result={}
    # hex字符串转bytes
    data = bytes.fromhex(value)
    if len(data)<5:
        return {
            "error":"3014长度不足"
        }
    # 输入
    input_names=[
        "IN1",
        "IN2",
        "IN3",
        "IN4",
        "IN5",
        "IN6",
        "IN7",
        "IN8"
    ]
    result["输入状态"]={}
    result["输入状态"].update(
        parse_3014_io_status(
            data[0],
            input_names[0:4],
            False
        )
    )
    result["输入状态"].update(
        parse_3014_io_status(
            data[1],
            input_names[4:8],
            False
        )
    )
    # 输出
    output_names=[
        "OUT1",
        "OUT2",
        "OUT3",
        "OUT4",
        "OUT5",
        "OUT6",
        "5V_OUT1",
        "5V_OUT2",
        "12V_OUT"
    ]
    result["输出状态"]={}
    result["输出状态"].update(
        parse_3014_io_status(
            data[2],
            output_names[0:4],
            True
        )
    )
    result["输出状态"].update(
        parse_3014_io_status(
            data[3],
            output_names[4:8],
            True
        )
    )
    result["输出状态"].update(
        parse_3014_io_status(
            data[4],
            output_names[8:9],
            True
        )
    )
    return result
#3014 输入输出状态表
def parse_3014_io_status(byte, names, output=False):
    result = {}
    status_map_input = {
        0:"不支持",
        1:"高电平",
        2:"低电平",
        3:"保留"
    }
    status_map_output = {
        0:"不支持",
        1:"高电平",
        2:"低电平",
        3:"悬空"
    }
    status_map = status_map_output if output else status_map_input
    for i,name in enumerate(names):
        # 每两个bit一个状态
        value = (byte >> (i*2)) & 0x03
        result[name] = status_map.get(
            value,
            "未知"
        )
    return result

# 4.32   附表_位置数据信息体 --->  4.36   附表_附加信息定义EE ---> 4.41   附表 扩展外设数据流
def parse_ee(payload):
    result = {}
    while len(payload) >= 6:
        func_id = payload[:4]
        length = int(payload[4:6], 16)
        value = payload[6:6 + length * 2]
        payload = payload[6 + length * 2:]
        if func_id == "3001":
            result["正反转状态"] = parse_3001(value)
        elif func_id == "3002":
            result["探头温度1"] = parse_3002(value)
        elif func_id == "3003":
            result["探头温度2"] = parse_3002(value)
        elif func_id == "3004":
            result["探头温度3"] = parse_3002(value)
        elif func_id == "3005":
            result["探头温度4"] = parse_3002(value)
        elif func_id == "300D":
            result["温度传感器"] = parse_300D(value)
        elif func_id == "3013":
            result["G-Sensor"] = parse_3013(value)
        elif func_id == "3014":
            result["输入和输出状态"] = parse_3014(value)      #0x3014	输入和输出状态
        else:
            result[f"未知_{func_id}"] = value
    return result

"""函数parse_tlv里是截取 3部分: id 长度 数据，
   parse_ea_0003 的总里程，它是两部分 ，类型和米数，于是数据错了 出现 if len(data) < 10 
   解决方法：使用 "parser":parse_ea_0003 直接调用函数
   """
# 4.37   附表_基础数据流
Map_解析EA下的所有ID = {
    "0003":{ "name":"总里程","parser":parse_ea_0003 },
    "0004":{ "name":"总油耗/总电耗", "parser":parse_ea_0004 },
    "0005":{ "name":"总运行时长", "parser":None },
    "0006":{ "name":"总熄火时长", "parser":None },
    "0007":{ "name":"总怠速时长", "parser":None },

    "0010":{ "name":"加速度表", "parser":parse_ea_0010 },
    "0011":{ "name":"车辆状态表", "parser":None },

    "0012":{ "name":"车辆电压", "parser":None },
    "0013":{ "name":"终端内置电池电压", "parser":None },
    "0014":{ "name":"CSQ值", "parser":None },
    "0015":{ "name":"车型ID", "parser":None },

    "0016":{ "name":"OBD协议类型", "parser":parse_ea_0016 },
    "0017":{ "name":"驾驶循环标签", "parser":None },
    "0018":{ "name":"GPS收星数", "parser":None },
    "0019":{ "name":"GPS位置精度", "parser":None },
    "001A":{ "name":"GPS平均信噪比", "parser":None },

    "001B":{ "name":"GPS天线状态", "parser":parse_ea_001B },
    "001D":{ "name":"设备拔出状态", "parser":parse_ea_001D },
    "001E":{ "name":"累计里程", "parser":None },

    "0020":{ "name":"点火类型", "parser":None },
    "0021":{ "name":"碳排放量", "parser":None },
    "0022":{ "name":"Roll角速度", "parser":None },
    "0023":{ "name":"Pitch角速度", "parser":None },
    "0024":{ "name":"Yaw角速度", "parser":None },
    "0025":{ "name":"累计里程2", "parser":None },
    "0026":{ "name":"输入状态", "parser":None },
    "0027":{ "name":"GPS定位解状态", "parser":None },
    "0028":{ "name":"设备运行时间", "parser":None },
    "0029":{ "name":"空调状态表", "parser":None }
}



# 4.36   附表 附加信息定义 0xE1 -- 0xFD 10个解析
# 意思：遇到 EA：不要直接解析数据进入下一层
Map_E1_to_EE = {
        "E1": {
            "name": "转速",
            "parser": None
        },
        "EA": {
            "name": "基础数据流",
            "children":{
                "id_bytes":2,
                "map":Map_解析EA下的所有ID
            }
        },
        "EB": {
            "name": "轿车扩展数据流",
            "parser": None
        },
        "EC": {
            "name": "货车扩展数据流",
            "parser": None
        },
        "ED": {
            "name": "新能源汽车数据",
            "parser": None
        },
        "EE": {
            "name": "扩展外设数据",
            "parser": parse_ee
        },
        "FA": {
            "name": "报警命令",
            "parser": None
        },
        "FB": {
            "name": "基站数据流",
            "parser": None
        },
        "FC": {
            "name": "WIFI数据流",
            "parser": None
        },
        "FD": {
            "name": "0205数据",
            "parser": None
        }
    }


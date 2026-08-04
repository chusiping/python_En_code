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

def parse_ea_0020(data):
    if len(data) < 4:
        return {
            "错误": "点火类型数据长度不足",
            "数据": data
        }
    value = int(data[:4], 16)
    result = {
        "原始值": "0x" + data[:4].upper(),
        "点火类型": {}
    }
    bit_map = {
        0: "ACC线点火",
        1: "安防监听点火",
        2: "GPS速度",
        3: "电压(低电压+震动)",
        4: "发动机车速转速",
        5: "ACC中断点火",
        6: "ADC中断点火",
        7: "电压(高电压)",
        8: "维修模式"
    }
    for bit, name in bit_map.items():
        if value & (1 << bit):
            result["点火类型"][name] = True
        else:
            result["点火类型"][name] = False
    return result

def parse_ea_0022(data):
    if len(data) < 4:
        return {
            "错误": "Roll角速度数据长度不足",
            "数据": data
        }
    raw = int(data[:4], 16)
    # bit15 符号
    negative = (raw & 0x8000) != 0
    # bit0-14 数值
    value = raw & 0x7FFF
    # 精度0.1
    speed = value / 10
    if negative:
        speed = -speed
        direction = "负方向"
    else:
        direction = "正方向"
    return {
        "原始值": "0x" + data[:4].upper(),
        "方向": direction,
        "数值": value,
        "角速度": speed,
        "单位": "dps"
    } 

def parse_ea_0025(data):
    if len(data) < 10:
        return {
            "错误": "累计里程2数据长度不足",
            "数据": data
        }
    # =====================
    # 累计类型
    # =====================
    type_code = data[0:2].upper()
    type_map = {
        "01": "GPS速度累计",
        "02": "OBD速度累计",
        "03": "OBD仪表累计"
    }
    # =====================
    # 累计里程
    # =====================
    mileage_hex = data[2:10]
    mileage = int(mileage_hex,16)
    return {
        "累计类型编码":
            "0x" + type_code,
        "累计类型":
            type_map.get(
                type_code,
                "未知类型"
            ),
        "累计里程":
            mileage,
        "单位":
            "米"
    }

def parse_ea_0026(data):
    if len(data) < 12:
        return {
            "错误": "D_IN状态数据长度不足",
            "数据": data
        }
    # 每2个HEX字符一个byte
    values = [
        int(data[i:i+2],16)
        for i in range(0,12,2)
    ]
    return {
        "D_IN2高输入": {
            "原始值": values[0],
            "状态": "检测到高" if values[0] == 1 else "无检测"
        },
        "D_IN3高输入": {
            "原始值": values[1],
            "状态": "检测到高" if values[1] == 1 else "无检测"
        },
        "D_IN4高输入": {
            "原始值": values[2],
            "状态": "检测到高" if values[2] == 1 else "无检测"
        },
        "D_IN5高输入": {
            "原始值": values[3],
            "状态": "检测到高" if values[3] == 1 else "无检测"
        },
        "D_IN6低输入": {
            "原始值": values[4],
            "状态": "检测到低" if values[4] == 1 else "无检测"
        },
        "D_IN7高输入": {
            "原始值": values[5],
            "状态": "检测到高" if values[5] == 1 else "无检测"
        }
    }

def parse_ea_0027(data):
    if len(data) < 2:
        return {
            "错误": "GPS定位解状态数据长度不足",
            "数据": data
        }
    value = data[:2].upper()
    status_map = {
        "00": "定位无效",
        "01": "普通定位",
        "02": "伪距差分定位(RTD)",
        "03": "未定义",
        "04": "RTK固定解",
        "05": "RTK浮点解",
        "06": "航迹推算"
    }
    return {
        "状态编码": "0x" + value,
        "GPS定位解状态":
            status_map.get(
                value,
                "未知状态"
            )
    }

def parse_ea_0029(data):
    if len(data) < 22:
        return {
            "错误": "空调状态数据长度不足",
            "数据": data
        }
    byte_data = [
        int(data[i:i+2],16)
        for i in range(0,16,2)
    ]
    return {
        "空调开关":
            "打开" if byte_data[0] & 0x01 else "关闭",
        "空调模式":
            parse_主驾空调模式(byte_data[1]),
        "主驾温度":
            parse_主驾温度解析(byte_data[2]),
        "副驾温度":
            parse_主驾温度解析(byte_data[3]),
        "风量":
            parse_风量等级(byte_data[4]),
        "出风模式":
            parse_出风模式(byte_data[5]),
        "特殊功能①":
            parse_特殊功能开关1(byte_data[6]),
        "特殊功能②":
            parse_特殊功能开关2(byte_data[7]),
        "空调定时关闭":
            {
                "时间":
                    byte_data[8],
                "单位":
                    "分钟"
            }     
    }

def parse_主驾空调模式(value):
    mode = {
        0x00:"未知",
        0x01:"自动模式",
        0x02:"制冷模式",
        0x03:"制热模式",
        0x04:"除湿模式",
        0x05:"送风模式"
    }
    return mode.get(
        value,
        "预留"
    )

def parse_主驾温度解析(value):
    if value == 0x00:
        return "未知"
    if value == 0xFF:
        return "自动"
    temp = value * 0.5 + 9.5
    return {
        "温度":temp,
        "单位":"℃"
    }

def parse_风量等级(value):
    if value == 0:
        return "未知"
    if value == 0xFF:
        return "自动"
    return {
        "等级":value+1
    }

def parse_出风模式(value):
    mode={
        0x00:"未知",
        0x01:"吹身子",
        0x02:"吹脚",
        0x03:"吹前风挡",
        0x04:"吹身子+吹脚",
        0x05:"吹前风挡+吹脚",
        0x06:"吹身子+吹前风挡",
        0x07:"吹身子+吹前风挡+吹脚"
    }
    return mode.get(
        value,
        "预留"
    )

def parse_特殊功能开关1(value):
    return {
        "A/C":
        {
            "支持":
                bool(value & 0x01),
            "开启":
                bool(value & 0x02)
        },
        "循环模式":
        {
            "支持":
                bool(value & 0x04),
            "模式":
                {
                    0:"关闭",
                    1:"内循环",
                    2:"外循环",
                    3:"内外循环同时打开/自动"
                }.get(
                    (value >> 4)&0x03,
                    "未知"
                )
        }
    }

def parse_特殊功能开关2(value):
    return {
        "前除雾":
        {
            "支持":
                bool(value & 0x01),
            "开启":
                bool(value & 0x02)
        },
        "后除雾":
        {
            "支持":
                bool(value & 0x04),
            "开启":
                bool(value & 0x08)
        },
        "双区同步":
        {
            "支持":
                bool(value & 0x10),
            "开启":
                bool(value & 0x20)
        }
    }

def parse_hex2int(data, unit=None, scale=1):
    if not data:
        return {
            "错误":"数据为空"
        }
    value = int(data,16)
    result = {
        "原始数据":data,
        "数值":value * scale
    }
    if unit:
        result["单位"] = unit
    return result

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


from parse_carextentdataflow import TRUCK_EXT_CONFIG

def parse_ec(hexstr):
    data = bytes.fromhex(hexstr) #把十六进制字符串转换成 Python 的 bytes（二进制字节）对象
    result={}
    index=0
    while index < len(data):
        # ID 两字节
        func_id=data[index:index+2].hex().upper()
        index+=2
        if index>=len(data):
            break
        # 长度
        length=data[index]
        index+=1
        # 数据
        value=data[index:index+length]
        index+=length
        cfg=TRUCK_EXT_CONFIG.get(func_id)
        if cfg:
            try:
                val=cfg["parser"](value)
            except Exception as e:
                val=f"解析错误:{e}"
            result[func_id]={
                "name":cfg["name"],
                "value":val,
                "unit":cfg.get("unit","")
            }
        else:
            result[func_id]={
                "name":"未知扩展",
                "raw":value.hex().upper()
            }
    return result


"""函数parse_tlv里是截取 3部分: id 长度 数据，
   parse_ea_0003 的总里程，它是两部分 ，类型和米数，于是数据错了 出现 if len(data) < 10 
   解决方法：使用 "parser":parse_ea_0003 直接调用函数
   """
# 4.37   附表_基础数据流
Map_解析EA下的所有ID = {
    "0003":{ "name":"总里程","parser":parse_ea_0003 },
    "0004":{ "name":"总油耗/总电耗", "parser":parse_ea_0004 },
    "0005":{ "name":"总运行时长",  "parser":lambda x: parse_hex2int(x,"秒")},
    "0006":{ "name":"总熄火时长", "parser":lambda x: parse_hex2int(x,"秒")},
    "0007":{ "name":"总怠速时长", "parser":lambda x: parse_hex2int(x,"秒")},

    "0010":{ "name":"加速度表", "parser":parse_ea_0010 },
    "0011":{ "name":"车辆状态表", "parser":parse_ea_0011 },

    "0012":{ "name":"车辆电压", "parser":lambda x: parse_hex2int(x,"0.1V")},
    "0013":{ "name":"终端内置电池电压", "parser":lambda x: parse_hex2int(x,"0.1V")},
    "0014":{ "name":"CSQ值", "parser":lambda x: parse_hex2int(x)},
    "0015":{ "name":"车型ID", "parser":None },

    "0016":{ "name":"OBD协议类型", "parser":parse_ea_0016 },
    "0017":{ "name":"驾驶循环标签", "parser":lambda x: parse_hex2int(x)},
    "0018":{ "name":"GPS收星数", "parser":lambda x: parse_hex2int(x)},
    "0019":{ "name":"GPS位置精度", "parser":lambda x: parse_hex2int(x,"0.01")},
    "001A":{ "name":"GPS平均信噪比", "parser":lambda x: parse_hex2int(x,"db")},

    "001B":{ "name":"GPS天线状态", "parser":parse_ea_001B },
    "001D":{ "name":"设备拔出状态", "parser":parse_ea_001D },
    "001E":{ "name":"累计里程", "parser":lambda x: parse_hex2int(x,"米")},

    "0020":{ "name":"点火类型", "parser":parse_ea_0020 },
    "0021":{ "name":"碳排放量(g)", "parser":lambda x: parse_hex2int(x,"克")},
    "0022":{ "name":"Roll角速度", "parser":parse_ea_0022 },
    "0023":{ "name":"Pitch角速度", "parser":parse_ea_0022 },    # 结构一样复用
    "0024":{ "name":"Yaw角速度", "parser":parse_ea_0022 },      # 结构一样复用

    "0025":{ "name":"累计里程2(SWD专用)", "parser":parse_ea_0025 },
    "0026":{ "name":"5高1低输入状态", "parser":parse_ea_0026 },

    "0027":{ "name":"GPS定位解状态", "parser":parse_ea_0027 },
    "0028":{ "name":"设备运行时间", "parser":lambda x: parse_hex2int(x,"秒")},
    "0029":{ "name":"空调状态表", "parser":parse_ea_0029 }
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
            "parser": parse_ec
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


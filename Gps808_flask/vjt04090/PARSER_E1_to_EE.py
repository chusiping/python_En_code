from codec import *



def parse_e1(data):
    return {}
def parse_eb(data):
    return {}
def parse_ec(data):
    return {}
def parse_ed(data):
    return {}
def parse_fa(data):
    return {}
def parse_fb(data):
    return {}
def parse_fc(data):
    return {}
def parse_fd(data):
    return {}
def parse_ea_0001(data):
    return {}
def parse_ea_0002(data):
    return {}



# 4.45   附表_基础数据项：总里程格式表 
def parse_ea_0003(data):
    if len(data) < 10:
        return {
            "错误": "总里程数据长度不足"
        }
    mileage_type = data[0:2]
    mileage = int.from_bytes(
        bytes.fromhex(data[2:10]),
        "big"
    )
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
        "单位": "米"
    }




def parse_ea(hexstr: str):
    hexstr = split_hex(hexstr)
    idx = 0
    result = []
    EA_PARSER = {
        "0001": {
            "name": "ACC ON时间",
            "parser": parse_ea_0001
        },
        "0002": {
            "name": "ACC OFF时间",
            "parser": parse_ea_0002
        },
        "0003": {
            "name": "总里程数据",
            "parser": parse_ea_0003
        }
    }
    # 功能ID定义
    func_map = {
        "0001": "预留",
        "0002": "预留",
        "0003": "总里程数据",
        "0004": "总油耗/总电耗",
        "0005": "总运行时长",
        "0006": "总熄火时长",
        "0007": "总怠速时长",
        "0008": "里程数据表",
        "0009": "油耗数据表",
        "0010": "加速度表",
        "0011": "车辆状态表",
        "0012": "车辆电压",
        "0013": "终端内置电池电压",
        "0014": "CSQ值",
        "0015": "车型ID",
        "0016": "OBD协议类型",
        "0017": "驾驶循环标签",
        "0018": "GPS收星数",
        "0019": "GPS位置精度",
        "001A": "GPS平均信噪比",
        "001B": "GPS天线状态",
        "001D": "设备拔出状态",
        "001E": "累计里程",
        "001F": "瞬时油耗",
        "0020": "点火类型",
        "0021": "碳排放量",
        "0022": "Roll角速度",
        "0023": "Pitch角速度",
        "0024": "Yaw角速度",
        "0025": "累计里程2",
        "0026": "输入状态",
        "0027": "GPS定位解状态",
        "0028": "设备运行时间",
        "0029": "空调状态表",
    }
    while idx < len(hexstr):
        # 功能ID
        func_id = hexstr[idx:idx+4]
        idx += 4
        if idx + 2 > len(hexstr):
            raise ValueError(
                f"EA长度字段缺失 func={func_id}"
            )
        # 数据长度 byte
        length = int(
            hexstr[idx:idx+2],
            16
        )
        idx += 2
        # 数据
        data = hexstr[
            idx:idx+length*2
        ]
        idx += length*2
        result.append(
            {
                "id": func_id,
                "name": func_map.get(
                    func_id,
                    "未知功能"
                ),
                "length": length,
                "data": data
            }
        )
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

EA_MAP = {
    "0001":{ "name":"预留", "parser":None },
    "0002":{ "name":"预留", "parser":None },
    "0003":{
        "name":"总里程",
        "children":{
            "id_bytes":1,
            "map":MILEAGE_MAP
        }
    },
    "0004":{ "name":"总油耗/总电耗", "parser":None },
    "0005":{ "name":"总运行时长", "parser":None },
    "0006":{ "name":"总熄火时长", "parser":None },
    "0007":{ "name":"总怠速时长", "parser":None },

    "0010":{ "name":"加速度表", "parser":None },
    "0011":{ "name":"车辆状态表", "parser":None },
    "0012":{ "name":"车辆电压", "parser":None },
    "0013":{ "name":"终端内置电池电压", "parser":None },
    "0014":{ "name":"CSQ值", "parser":None },
    "0015":{ "name":"车型ID", "parser":None },
    "0016":{ "name":"OBD协议类型", "parser":None },
    "0017":{ "name":"驾驶循环标签", "parser":None },
    "0018":{ "name":"GPS收星数", "parser":None },
    "0019":{ "name":"GPS位置精度", "parser":None },
    "001A":{ "name":"GPS平均信噪比", "parser":None },
    "001B":{ "name":"GPS天线状态", "parser":None },
    "001D":{ "name":"设备拔出状态", "parser":None },
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
Map_E1_to_EE = {
        "E1": {
            "name": "转速",
            "parser": parse_e1
        },
        "EA": {
            "name": "基础数据流",
            "children":{
                "id_bytes":2,
                "map":EA_MAP
            }
        },
        "EB": {
            "name": "轿车扩展数据流",
            "parser": parse_eb
        },
        "EC": {
            "name": "货车扩展数据流",
            "parser": parse_ec
        },
        "ED": {
            "name": "新能源汽车数据",
            "parser": parse_ed
        },
        "EE": {
            "name": "扩展外设数据",
            "parser": parse_ee
        },
        "FA": {
            "name": "报警命令",
            "parser": parse_fa
        },
        "FB": {
            "name": "基站数据流",
            "parser": parse_fb
        },
        "FC": {
            "name": "WIFI数据流",
            "parser": parse_fc
        },
        "FD": {
            "name": "0205数据",
            "parser": parse_fd
        }
    }


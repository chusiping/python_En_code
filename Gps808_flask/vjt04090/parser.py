from codec import *
import struct

# 第一处修改：增加消息分发 增加一个入口：
def parse_0200(hexstr: str):
    hexstr = split_hex(hexstr) #去空格去换行转大写
    idx = 0
    def take(n):
        nonlocal idx
        v = hexstr[idx:idx+n]
        idx += n
        return v
    result = []
    # ------- 开始解析 -------
    # result.append((take(2), "起始位"))
    msg_id = take(4)
    result.append((msg_id, "消息ID"))
    result.append((take(4), "消息体属性"))
    result.append((take(12), "终端手机号（BCD）"))
    result.append((take(4), "流水号"))
    result.append((take(8), "报警标志"))
    result.append((take(8), "状态"))
    if msg_id != "0200":
        raise ValueError(
            f"不是0200消息，收到:{msg_id}"
        )
    lat_hex = take(8)
    result.append((lat_hex, f"纬度)"))
    lng_hex = take(8)
    result.append((lng_hex, f"经度"))
    result.append((take(4), "海拔"))
    result.append((take(4), "速度"))
    result.append((take(4), "方向"))
    result.append((take(12), "时间"))
    # ===== 附加项解析（直到校验在前一个字节，最后一个是7E） =====
    while idx < len(hexstr)-2:
        # VJT扩展
        if hexstr[idx:idx+2]=="30":
            func_id = take(4)
            length = int(take(2),16)
            data = take(length*2)
            result.append(
                (
                    func_id,
                    data,
                    "扩展外设"
                )
            )
        else:
            item_id = take(2)
            length = int(take(2),16)
            data = take(length*2)
            result.append(
                (
                    item_id,
                    data,
                    "标准附加"
                )
            )
    # 校验码
    result.append((take(2), "校验码"))
    # 结束位
    # result.append((take(2), "结束位"))
    return result

def parse_jt808_packet(hexstr):
    hexstr = split_hex(hexstr)
    # 去掉7E
    if hexstr.startswith("7E"):
        hexstr = hexstr[2:]
    if hexstr.endswith("7E"):
        hexstr = hexstr[:-2]
    # 前4位就是消息ID
    msg_id = hexstr[:4]
    if msg_id == "0200":
        return parse_0200(hexstr)
    elif msg_id == "0900":
        return parse_0900(hexstr)
    elif msg_id == "8001":
        return parse_8001(hexstr)
    else:
        return {
            "msg_id": msg_id,
            "raw":hexstr
        }
    
def parse_0900(hexstr):
    result={}
    msg_id=hexstr[:4]   # 消息ID
    body=hexstr[4:]     # 跳过消息ID
    body_attr=body[:4]  # 消息体属性
    body_len = int(body_attr, 16) & 0x03FF     #  新增这一句 JT808消息体长度(低10位)
    phone=body[4:16]    # 手机号
    sn=body[16:20]      # 流水号
    data = body[20:20 + body_len * 2]      # 透传数据 这里只取消息体，不要把校验码取进来

    func_id=data[:2]
    result["消息ID"]="0900"
    result["功能ID"]="0x"+func_id
    payload=data[2:]
    if func_id=="F1":
        result["类型"]="车辆行程数据"
        result.update(parse_f1(payload))
    elif func_id=="F2":
        result["类型"]="车辆故障码"
        result.update(parse_f2(payload))
    elif func_id=="F3":
        result["类型"]="睡眠进入"
        result.update(parse_f3(payload))
    elif func_id=="F4":
        result["类型"]="睡眠唤醒"
    elif func_id=="F6":
        result["类型"]="MCU升级状态"
    elif func_id=="F7":
        result["类型"]="碰撞报警"
        result.update(parse_f7(payload))
    # result["数据"]=payload
    return result

def parse_8001(body):

    result_map = {
        0: "成功",
        1: "失败",
        2: "消息有误",
        3: "不支持",
        4: "报警处理确认"
    }

    if len(body) < 10:
        return {"error":"消息体长度不足"}

    reply_serial = int(body[0:4],16)

    reply_msgid = body[4:8]

    reply_result = int(body[8:10],16)

    return {
        "应答流水号": reply_serial,
        "应答消息ID": reply_msgid,
        "结果": reply_result,
        "结果说明": result_map.get(reply_result,"未知")
    }


def parse_f2(payload):

    result = {}

    # 长度至少要有：时间(6)+纬度(4)+经度(4)+数量(1)=15字节
    if len(payload) < 30:
        return {"error": "F2数据长度不足"}

    # 时间
    result["故障时间"] = parse_bcd_time(payload[0:12])

    # 纬度
    result["纬度"] = parse_lat(payload[12:20])

    # 经度
    result["经度"] = parse_lng(payload[20:28])

    # DTC数量
    dtc_num = int(payload[28:30], 16)
    result["故障码数量"] = dtc_num

    # DTC列表
    dtc_list = []

    pos = 30
    for i in range(dtc_num):

        if pos + 8 > len(payload):
            break

        dtc = payload[pos:pos + 8]
        dtc_list.append(dtc)

        pos += 8

    result["故障码"] = dtc_list

    return result

def parse_f3(payload):

    yy = int(payload[0:2])
    mm = int(payload[2:4])
    dd = int(payload[4:6])
    hh = int(payload[6:8])
    mi = int(payload[8:10])
    ss = int(payload[10:12])

    return {
        "休眠进入时间": f"20{yy:02d}-{mm:02d}-{dd:02d} {hh:02d}:{mi:02d}:{ss:02d}"
    }

def parse_f7(data):

    result={}


    # 时间
    result["碰撞时间"] = parse_bcd_time(
        data[0:12]
    )


    # 纬度
    lat = int.from_bytes(
        bytes.fromhex(data[12:20]),
        "big"
    )

    south = lat & 0x80000000

    lat &= 0x7fffffff

    result["纬度"] = lat / 1000000


    # 经度
    lng = int.from_bytes(
        bytes.fromhex(data[20:28]),
        "big"
    )

    west = lng & 0x80000000

    lng &= 0x7fffffff

    result["经度"] = lng / 1000000


    # 采样频率
    freq=int.from_bytes(
        bytes.fromhex(data[28:36]),
        "big"
    )

    result["采样周期(ms)"]=freq


    # 碰撞等级
    level=data[36:38]

    result["碰撞等级"]={
        "00":"轻微",
        "01":"中度",
        "02":"严重"
    }.get(level,"未知")


    return result


def parse_f1(payload):

    result={}


    while payload:


        # 信息ID
        info_id = payload[:4]

        # 长度
        length = int(payload[4:6],16)


        # 数据
        value = payload[6:6+length*2]


        # 下一组
        payload = payload[6+length*2:]


        if info_id=="0001":

            result["ACC ON时间"] = parse_bcd_time(value)


        elif info_id=="0002":

            result["ACC OFF时间"] = parse_bcd_time(value)


        elif info_id=="0003":

            result["ACC ON纬度"] = parse_lat(value)


        elif info_id=="0004":

            result["ACC ON经度"] = parse_lng(value)


        elif info_id=="0005":

            result["ACC OFF纬度"] = parse_lat(value)


        elif info_id=="0006":

            result["ACC OFF经度"] = parse_lng(value)


        elif info_id=="0007":

            result["驾驶循环标签"] = parse_u16(value)


        elif info_id=="0008":

            result["里程类型"] = {
                "01":"GPS累计里程",
                "07":"OBD仪表里程",
                "08":"OBD速度里程"
            }.get(value,"其他")


        elif info_id=="0009":

            result["行程里程(m)"] = parse_u32(value)


        elif info_id=="000A":

            result["总耗油(ml)"] = parse_u32(value)


        elif info_id=="000B":

            result["行程总时长(s)"] = parse_u32(value)


        elif info_id=="000C":

            result["超速时长(s)"] = parse_u16(value)


        elif info_id=="000D":

            result["超速次数"] = parse_u16(value)


        elif info_id=="000E":

            result["平均速度(km/h)"] = int(value,16)


        elif info_id=="000F":

            result["最高速度(km/h)"] = int(value,16)


        elif info_id=="0010":

            result["怠速时长(s)"] = parse_u32(value)


        elif info_id=="0011":

            result["是否支持刹车统计"] = value=="01"


        elif info_id=="0012":

            result["刹车次数"] = parse_u16(value)


        elif info_id=="0013":

            result["急加速次数"] = parse_u32(value)


        elif info_id=="0014":

            result["急减速次数"] = parse_u32(value)


        elif info_id=="0015":

            result["急转弯次数"] = parse_u32(value)

        elif info_id=="0016":

            result["低速里程(<20km/h)(m)"] = parse_u32(value)


        elif info_id=="0017":

            result["20-40km/h里程(m)"] = parse_u32(value)


        elif info_id=="0018":

            result["40-60km/h里程(m)"] = parse_u32(value)


        elif info_id=="0019":

            result["60-80km/h里程(m)"] = parse_u32(value)


        elif info_id=="001A":

            result["80-100km/h里程(m)"] = parse_u32(value)


        elif info_id=="001B":

            result["100-120km/h里程(m)"] = parse_u32(value)


        elif info_id=="001C":

            result[">120km/h里程(m)"] = parse_u32(value)

        elif info_id=="001D":

            result["怠速油耗(ml)"] = parse_u32(value)



        else:

            result[f"未知_{info_id}"] = value


    return result

# 扩展外设数据流不是一个独立的 JT808 消息包，它通常是挂在某个 JT808 消息里面的附加数据。
# 0200 消息里面有附加信息
def parse_external_441(payload):
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
        else:
            result[f"未知_{func_id}"] = value
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

def parse_ea(hexstr: str):
    """
    VJT基础数据流 EA解析
    格式:
    功能ID(2byte) + 长度(1byte) + 数据(Nbyte)
    输入:
        000305010570B9B70004050F036E5D54
    返回:
        [
            {
                "id":"0003",
                "name":"总里程数据",
                "length":5,
                "data":"010570B9B7"
            }
        ]
    """
    hexstr = split_hex(hexstr)
    idx = 0
    result = []
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

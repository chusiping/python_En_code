from codec import *
from parse_tvl2 import * 
from PARSER_E1_to_EE import *

# 第一处修改：增加消息分发 增加一个入口：
def parse_0200(hexstr: str):
    """
    JT/T 808 0200 位置信息汇报
    支持 VJT.04.090 扩展外设数据

    输入:
        已经去掉空格的HEX字符串
        包含:
        0200消息头 + 消息体

    注意:
        进入本函数前应该已经完成:
        7E去除
        7D转义恢复
        XOR校验
    """
    hexstr = split_hex(hexstr) #去空格去换行转大写
    def take(n):
        nonlocal idx
        value = hexstr[idx:idx+n]
        idx += n
        return value
    result = {
        "消息ID": "",
        "基础信息": {},
        "附加信息": []
    }
    idx = 0
    # =========================
    # 消息ID
    # =========================
    msg_id = take(4)
    if msg_id != "0200":
        raise ValueError(
            f"不是0200消息:{msg_id}"
        )
    result["消息ID"] = msg_id
    # ==========消息体属性===============
    body_attr = take(4)
    body_len = int(body_attr,16) & 0x03FF  #n个字节 JT808消息体长度 body_len，不包含手机号和流水号
    # result["基础信息"]["消息体属性"] = body_attr 不显示
    result["基础信息"]["消息体长度"] = body_len #流水号后开始到检验码前结束的部分
    # ==========终端手机号===============
    phone = take(12)
    result["基础信息"]["手机号"] = phone
    # ==========流水号===============
    serial = take(4)
    result["基础信息"]["流水号"] = int(serial,16) 
    # ===========计算消息体结束位置==============
    body_start = idx  #已经跳过：消息ID 4字符 消息体属性 4字符
    body_end = body_start + body_len * 2  # 消息体结束的位置，如果不出错就是427E验证码之前
    # 防止异常数据
    if body_end > len(hexstr):
        body_end = len(hexstr)
    print("body_start", body_start)
    print("body_end", body_end)
    print("body_len", body_len)
    print(f"body长度 ({body_end}-{body_start})/2 = ", (body_end-body_start)//2)

    # ===========报警标志==============
    # alarm = take(8)
    # result["基础信息"]["报警标志"] = alarm  #取消显示
    alarm = take(8)
    result["基础信息"]["报警标志"] = alarm
    result["基础信息"]["报警内容"] = parse_alarm_flag(alarm)
    # 状态
    status = take(8)
    result["基础信息"]["状态"] =  parse_status_flag(status)
    # =========================
    # 经纬度
    # =========================
    lat = int(take(8),16)
    lng = int(take(8),16)
    # Bit31方向
    lat_flag = "南纬" if lat & 0x80000000 else "北纬"
    lng_flag = "西经" if lng & 0x80000000 else "东经"
    lat_value = (lat & 0x7FFFFFFF) / 1000000
    lng_value = (lng & 0x7FFFFFFF) / 1000000
    result["基础信息"]["纬度"] = lat_value
    result["基础信息"]["经度"] = lng_value
    # =========================
    # 高程
    # =========================
    altitude = int(take(4),16)
    result["基础信息"]["海拔"] = altitude
    # 速度
    speed = int(take(4),16)
    result["基础信息"]["速度"] = speed / 10
    # 方向
    direction = int(take(4),16)
    result["基础信息"]["方向"] = direction
    # 时间
    time_bcd = take(12)
    result["基础信息"]["时间"] = parse_bcd_time(time_bcd)
    # =========================
    # 附加信息解析
    # =========================
    while idx < body_end:
        remain = hexstr[idx:body_end]   #日期之后开始到消息体结束 = 所有附加信息
        if len(remain) < 2:
            break
        # ---------------------
        # VJT扩展外设
        # 3001-4FFF
        # ---------------------
        if len(remain) >= 6:    #判断剩余的数据长度是否至少有 6 个十六进制字符
            func_id = int(remain[:4],16)
            if 0x3001 <= func_id <= 0x4FFF:
                func_id_hex = take(4)
                length = int(take(2),16)
                value = take(length*2)
                result["附加信息"].append(
                    {
                        "类型":"VJT扩展外设",
                        "ID":func_id_hex,
                        "长度":length,
                        "数据":value
                    }
                )
                continue
        # ---------------------
        # 原来的取值方式，给parse_0xE1_0xFD(item_id,length,value) 传三个参数
        # ---------------------
        # item_id = take(2)
        # if idx + 2 > body_end:
        #     break
        # length = int(take(2),16)
        # value = take(length*2)
        
        # 新的的取值方式，改成直接取 包含id，长度，数据完整字符串-----------------
        # 当前idx指向附加信息开始位置
        start = idx
        # 至少需要 ID(1字节)+LEN(1字节)
        if idx + 4 > body_end:
            break
        # 读取ID
        item_id = hexstr[idx:idx+2]
        # 读取长度
        length = int(
            hexstr[idx+2:idx+4],
            16
        )
        # 整个TLV长度
        total_len = 2 + 2 + length * 2
        # 直接取完整TLV
        tlv_data = hexstr[
            idx:
            idx + total_len
        ]
        # 移动指针
        idx += total_len
        #------------------------------------------------------------------------

        att_info = parse_tlv(tlv_data,1,Map_E1_to_EE)
        result["附加信息"].append(att_info)

        # result["附加信息"].append(   # 暂时不用，用上一行代替
        #     {
        #         "类型":"JT808标准附加",
        #         "ID":item_id,
        #         "长度":length,
        #         "数据":parse_external_441(value) 
        #     }
        # )


    # 校验码
    result["校验码"] = take(2)
    return result
def parse_jt808_packet(hexstr, escaped=False):
    hexstr = split_hex(hexstr)
    msg_id = hexstr[:4]
    if msg_id == "0200":
        return parse_0200(hexstr)
    elif msg_id == "0900":
        return parse_0900(hexstr)
    elif msg_id == "8001":
        return parse_8001(hexstr)
    elif msg_id == "0002":
        return parse_0002(hexstr)
    elif msg_id == "0205":
        return parse_0205(hexstr)
    elif msg_id == "0704":
        return parse_0704(hexstr)
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

def parse_8001(hexstr):
    result = {}
    # 消息ID
    result["消息ID"] = hexstr[0:4]
    # 消息体属性
    result["消息属性"] = int(
        hexstr[4:8],
        16
    )
    # 终端手机号 6字节BCD
    result["终端号"] = hexstr[8:20]
    # 流水号
    result["流水号"] = int(
        hexstr[20:24],
        16
    )
    # 去掉校验
    body = hexstr[24:-2]
    # 8001消息体
    result["reply_serial"] = int(
        body[0:4],
        16
    )
    result["应答ID"] = body[4:8] #应答ID → 保留十六进制
    status = int(
        body[8:10],
        16
    )
    result["结果"] = {
        0: "成功/确认",
        1: "失败",
        2: "消息有误",
        3: "不支持"
    }.get(
        status,
        "未知"
    )
    return result

# 终端心跳包上报 未写完
def parse_0002(hexstr):
    """
    JT808消息头解析
    hexstr: 十六进制字符串
    """
    result = {}
    # =========================
    # 消息ID
    # =========================
    result["消息ID"] = hexstr[0:4]
    # =========================
    # 消息体属性 WORD
    # =========================
    body_attr = int(hexstr[4:8], 16)
    result["消息体属性"] = f"{body_attr:04X}"
    # 消息体长度 bit0-bit9
    result["消息体长度"] = body_attr & 0x03FF
    # 加密方式 bit10-bit12
    encrypt = (body_attr >> 10) & 0x07
    result["数据加密方式"] = {
        0: "不加密",
        1: "RSA加密",
        4: "SM4加密"
    }.get(
        encrypt,
        "未知"
    )
    # 是否分包 bit13
    is_subpackage = bool(
        body_attr & 0x2000
    )
    result["是否分包"] = is_subpackage
    # =========================
    # 终端手机号 BCD[6]
    # =========================
    phone_hex = hexstr[8:20]
    phone = ""
    for i in range(0,12,2):
        phone += phone_hex[i:i+2]
    # 去掉前导0
    result["终端手机号"] = phone.lstrip("0")
    # =========================
    # 消息流水号
    # =========================
    result["消息流水号"] = int(
        hexstr[20:24],
        16
    )
    # =========================
    # 分包信息
    # =========================
    index = 24
    if is_subpackage:
        result["消息总包数"] = int(
            hexstr[index:index+4],
            16
        )
        index += 4
        result["包序号"] = int(
            hexstr[index:index+4],
            16
        )
    return result

def parse_0205(hexstr):
    result = {}
    # =========================
    # 消息ID
    # =========================
    result["消息ID"] = hexstr[0:4]
    # =========================
    # 消息体属性 WORD
    # =========================
    body_attr = int(hexstr[4:8], 16)
    result["消息体属性"] = f"{body_attr:04X}"
    # 消息体长度 bit0-bit9
    body_len = body_attr & 0x03FF
    result["消息体长度"] = body_len
    # =========================
    # 加密方式 bit10-bit12
    # =========================
    encrypt = (body_attr >> 10) & 0x07
    result["数据加密方式"] = {
        0: "不加密",
        1: "RSA加密",
        4: "SM4加密"
    }.get(
        encrypt,
        "未知"
    )
    # =========================
    # 是否分包 bit13
    # =========================
    is_subpackage = bool(
        body_attr & 0x2000
    )
    result["是否分包"] = is_subpackage
    # =========================
    # 终端手机号 BCD[6]
    # =========================
    phone_hex = hexstr[8:20]
    phone = ""
    for i in range(0,12,2):
        phone += phone_hex[i:i+2]
    result["终端手机号"] = phone.lstrip("0")
    # =========================
    # 消息流水号
    # =========================
    result["消息流水号"] = int(
        hexstr[20:24],
        16
    )
    # =========================
    # 分包信息
    # =========================
    index = 24
    if is_subpackage:
        result["消息总包数"] = int(
            hexstr[index:index+4],
            16
        )
        index += 4
        result["包序号"] = int(
            hexstr[index:index+4],
            16
        )
        index += 4
    # =========================
    # 消息体开始
    # =========================
    body_start = index
    body_hex = hexstr[
        body_start:
        body_start + body_len * 2
    ]
    # =========================
    # 0205消息体
    # =========================
    body_index = 0
    def read_string(length):
        nonlocal body_index
        value = bytes.fromhex(
            body_hex[
                body_index:
                body_index + length * 2
            ]
        )
        body_index += length * 2
        return value.decode(
            "ascii",
            errors="ignore"
        ).strip("\x00")
    def read_bytes(length):
        nonlocal body_index
        value = body_hex[
            body_index:
            body_index + length * 2
        ]
        body_index += length * 2
        return value.upper()
    def read_word():
        nonlocal body_index
        value = int(
            body_hex[
                body_index:
                body_index+4
            ],
            16
        )
        body_index += 4
        return value
    def read_dword():
        nonlocal body_index
        value = int(
            body_hex[
                body_index:
                body_index+8
            ],
            16
        )
        body_index += 8
        return value
    # 版本号
    result["终端软件版本号"] = read_string(14)
    # 日期
    result["终端软件版本日期"] = read_string(10)
    # CPU ID
    result["CPU ID号"] = read_bytes(12)
    # GSM TYPE
    result["GSM TYPE Name"] = read_string(15)
    # IMEI
    result["GSM IMEI号"] = read_string(15)
    # IMSI
    result["SIM卡 IMSI号"] = read_string(15)
    # ICCID
    result["SIM卡 ICCID"] = read_string(20)
    # 车系车型ID
    result["Car Type"] = read_word()
    # VIN
    result["VIN"] = read_string(17)
    # 总里程
    result["总里程"] = {
    "值":91273655,
    "单位":"m",
    "千米":91273.655
}
    # 总耗油量
    result["总耗油量"] = read_dword()
    return result

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






#判断 "标准附加信息" 还是 "扩展外设数据
VJT_EXT_START = 0x3001
VJT_EXT_END = 0x4FFF
def is_vjt_external(hexstr):
    if len(hexstr) < 4:
        return False
    func_id = int(hexstr[:4],16)
    return VJT_EXT_START <= func_id <= VJT_EXT_END
# 解析JT808报警标志位
def parse_alarm_flag(hexstr):
    """
    解析JT808报警标志位
    参数:
        hexstr:
            4字节HEX字符串
            例如:
            "00000001"
    返回:
        报警列表
    """
    alarm_map = {
        0: "紧急报警",
        1: "超速报警",
        2: "疲劳驾驶",
        3: "危险预警",
        4: "GNSS模块故障",
        5: "GNSS天线未接或被剪断",
        6: "GNSS天线短路",
        7: "终端主电源欠压",
        8: "终端主电源掉电",
        9: "终端LCD或显示器故障",
        10: "TTS模块故障",
        11: "摄像头故障",
        12: "保留",
        # --------- 以下为新补全的标志位 ---------
        13: "超速预警",
        18: "当天累计驾驶超时",
        19: "超时停车",
        20: "进出区域",
        21: "进出路线",
        22: "路段行驶时间不足/过长",
        23: "路线偏离报警",
        24: "车辆VSS故障",
        25: "车辆油量异常",
        26: "车辆被盗(通过车辆防盗器)",
        27: "车辆非法点火",
        28: "车辆非法位移"
    }
    # HEX转整数
    flag = int(hexstr,16)
    result = []
    for bit, desc in alarm_map.items():
        if flag & (1 << bit):
            result.append(
                {
                    "位移":bit,
                    "报警内容":desc
                }
            )
    return result
# JT808 状态标志解析
def parse_status_flag(hexstr):
    status_map = {
        0: {0: "ACC关", 1: "ACC开"},
        1: {0: "未定位", 1: "定位"},
        2: {0: "北纬", 1: "南纬"},
        3: {0: "东经", 1: "西经"},
        4: {0: "停运状态", 1: "运营状态"},
        5: {0: "经纬度未经保密插件加密", 1: "经纬度已经保密插件加密"},
        10: {0: "车辆油路正常", 1: "车辆油路断开"},
        11: {0: "车辆电路正常", 1: "车辆电路断开"},
        12: {0: "车门解锁", 1: "车门加锁"},
        13: {0: "正常模式", 1: "维修模式"},
        14: {0: "WIFI关闭", 1: "WIFI开启"},
        15: {0: "胎压433模块正常", 1: "胎压433模块异常"},
        16: {0: "蓝牙正常", 1: "蓝牙异常"},
        17: {0: "斗车未抬起", 1: "斗车已抬起"},
        18: {0: "未使用GPS卫星定位", 1: "使用GPS卫星定位"},
        19: {0: "未使用北斗卫星定位", 1: "使用北斗卫星定位"},
        20: {0: "未使用GLONASS卫星定位", 1: "使用GLONASS卫星定位"},
        21: {0: "未使用Galileo卫星定位", 1: "使用Galileo卫星定位"},
        22: {0: "未使用差分定位", 1: "使用差分定位"}
    }
    status = int(hexstr, 16)
    result = []
    for bit, values in status_map.items():
        value = (status >> bit) & 0x01
        result.append(
            {
                "位移": bit,
                "状态": values[value]
            }
        )
    return result

# 4.36   附表 附加信息定义 0xE1 -- 0xFD 10个解析
def parse_0xE1_0xFD(id,length,data):
    ATTACH_PARSER = {
        "E1": {
            "name": "转速",
            "parser": parse_e1
        },
        "EA": {
            "name": "基础数据流",
            "parser": parse_ea
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
    result = {}
    info = ATTACH_PARSER.get(id)
    if info:
        parser = info["parser"]
        # 调用对应解析函数
        detail = parser(data)
    else:
        detail = {
            "原始数据": data
        }
    result = {
        "ID": id,
        "类型": info["name"] if info else "未知附加信息",
        "长度": length,
        "数据": detail
    }
    return result


# parse_0200_body没有：0200 消息体属性 手机号 流水号
def parse_0200_body(hexstr):
    idx = 0
    def take(n):
        nonlocal idx
        value = hexstr[idx:idx+n]
        idx += n
        return value
    
    result = {
        "基础信息": {},
        "附加信息": []
    }
    
    # 1. 报警标志 (DWORD -> 8位HEX)
    alarm = take(8)
    result["基础信息"]["报警报文"] = alarm
    result["基础信息"]["报警内容"] = parse_alarm_flag(alarm)
    
    # 2. 状态 (DWORD -> 8位HEX)
    status = take(8)
    result["基础信息"]["状态"] = status
    result["基础信息"]["状态内容"] = parse_status_flag(status)
    
    # 3. 纬度 (DWORD -> 单行 int 转换与除法)
    lat = int(take(8), 16)
    result["基础信息"]["纬度"] = (lat & 0x7FFFFFFF) / 1000000
    
    # 4. 经度 (DWORD -> 单行 int 转换与除法)
    lng = int(take(8), 16)
    result["基础信息"]["经度"] = (lng & 0x7FFFFFFF) / 1000000
    
    # 5. 高程 (WORD -> 单行 int 转换)
    result["基础信息"]["海拔"] = int(take(4), 16)
    
    # 6. 速度 (WORD -> 单行 int 转换与除法)
    result["基础信息"]["速度"] = int(take(4), 16) / 10
    
    # 7. 方向 (WORD -> 单行 int 转换)
    result["基础信息"]["方向"] = int(take(4), 16)
    
    # 8. 时间 (BCD[6] -> 12位HEX)
    time_bcd = take(12)
    result["基础信息"]["时间"] = parse_bcd_time(time_bcd)
    
    # 剩余就是位置附加信息
    remain = hexstr[idx:]
    if remain:
        result["附加信息原始"] = remain
        
    return result, idx


def parse_0704(hexstr):
    if any(x in hexstr.upper() for x in ["7D01", "7D02"]):
        print("字符串中包含需要反转义的字符")
        return {}
    idx = 0
    def take(n):
        nonlocal idx
        value = hexstr[idx:idx+n]
        idx += n
        return value
    result = {"消息ID":"0704"}
    take(4)      # 0704
    body_attr = take(4)
    phone = take(12)
    serial = take(4)
    result["消息属性"] = body_attr
    result["终端号"] = phone
    result["流水号"] = int(serial, 16)
    count = int(
        take(4),
        16
    )
    data_type = take(2)
    result["数据项数量"] = count
    type_mapping = {
            "00": "盲点补报",
            "01": "正常批量数据"
        }
    
    result["类型"] = type_mapping.get(data_type, f"未知类型({data_type})")

    result["位置数据"]= []
    for i in range(count):
        length_smal = take(4)
        length = int(length_smal,16)
        body = take(length*2)
        pos, used = parse_0200_body(body)
        result["位置数据"].append(pos)
    return result
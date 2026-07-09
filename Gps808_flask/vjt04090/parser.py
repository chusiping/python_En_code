from codec import *

# 第一处修改：增加消息分发 增加一个入口：
def parse_gps_packet(hexstr: str):
    hexstr = split_hex(hexstr)

    idx = 0
    def take(n):
        nonlocal idx
        v = hexstr[idx:idx+n]
        idx += n
        return v

    result = []

    # ------- 开始解析 -------
    result.append((take(2), "起始位"))
    msg_id = take(4)
    result.append(msg_id, "消息ID")
    result.append((take(4), "消息体属性"))

    result.append((take(12), "终端手机号（BCD）"))
    result.append((take(4), "流水号"))

    result.append((take(8), "报警标志"))
    result.append((take(8), "状态"))

    if msg_id != "0200":
        raise ValueError(
            f"不是0200消息，收到:{msg_id}"
        )

    # ---- 纬度 ----
    lat_len = 8
    if '7D' in hexstr[idx:idx+8] or '7E' in hexstr[idx:idx+8]:
        lat_len = 10  # 转义了，实际占 5 字节 = 10 hex
    lat_hex = take(lat_len)
    result.append((lat_hex, f"纬度 (hex length={lat_len})"))

    # ---- 经度 ----
    lng_len = 8
    if '7D' in hexstr[idx:idx+8] or '7E' in hexstr[idx:idx+8]:
        lng_len = 10  # 转义了
    lng_hex = take(lng_len)
    result.append((lng_hex, f"经度 (hex length={lng_len})"))

    result.append((take(4), "海拔"))
    result.append((take(4), "速度"))
    result.append((take(4), "方向"))

    result.append((take(12), "时间（BCD）"))

    # ===== 附加项解析（直到校验在前一个字节，最后一个是7E） =====
    while idx < len(hexstr) - 4:  # 最后两个字节是 校验 + 7E
        item_id = take(2)
        item_len = int(take(2), 16)
        item_data = take(item_len * 2)
        result.append((item_id + item_len.to_bytes(1, 'big').hex().upper() + item_data, f"附加项 0x{item_id}"))

    # 校验码
    result.append((take(2), "校验码"))

    # 结束位
    result.append((take(2), "结束位"))

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
        return parse_gps_packet(
            "7E" + hexstr + "7E"
        )


    elif msg_id == "0900":
        return parse_0900(hexstr)


    elif msg_id == "8900":
        return parse_8900(hexstr)


    else:
        return {
            "msg_id": msg_id,
            "raw":hexstr
        }
    
def parse_0900(hexstr):
    result={}
    # 消息ID
    msg_id=hexstr[:4]
    # 跳过消息ID
    body=hexstr[4:]
    # 消息体属性
    body_attr=body[:4]
    # 手机号
    phone=body[4:16]
    # 流水号
    sn=body[16:20]
    # 透传数据
    data=body[20:]
    func_id=data[:2]
    result["消息ID"]="0900"
    result["功能ID"]="0x"+func_id
    payload=data[2:]
    if func_id=="F1":
        result["类型"]="车辆行程数据"
    elif func_id=="F2":
        result["类型"]="车辆故障码"
    elif func_id=="F3":
        result["类型"]="睡眠进入"
    elif func_id=="F4":
        result["类型"]="睡眠唤醒"
    elif func_id=="F6":
        result["类型"]="MCU升级状态"
    elif func_id=="F7":
        result["类型"]="碰撞报警"
    result["数据"]=payload
    return result
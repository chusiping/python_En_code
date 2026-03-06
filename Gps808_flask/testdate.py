from datetime import datetime
import random
import math

def split_hex(hexstr):
    hexstr = hexstr.replace(" ", "").replace("\n", "")
    return hexstr.upper()

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
    result.append((take(4), "消息ID"))
    result.append((take(4), "消息体属性"))

    result.append((take(12), "终端手机号（BCD）"))
    result.append((take(4), "流水号"))

    result.append((take(8), "报警标志"))
    result.append((take(8), "状态"))

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


def pretty_print(result):
    for val, desc in result:
        print(f"    {val:<20} {desc}")

def jt808_parse_location(lat_hex: str, lng_hex: str, speed_hex: str, direction_hex: str,altitude_hex: str,
                         ext_01_hex: str = None, ext_03_hex: str = None, ext_25_hex: str = None):
    """
    将 JT808 4字节经纬度（hex）转换成浮点度数。
    参数示例：
        lat_hex = "01617C72"
        lng_hex = "06C1B888"
    """
    lat = int(lat_hex, 16) / 1_000_000
    lng = int(lng_hex, 16) / 1_000_000
    speed = int(speed_hex, 16) / 10          # km/h
    direction = int(direction_hex, 16)       # 0-359°
    altitude = int(altitude_hex, 16)        
    result = {
        "维度": lat,
        "经度": lng,
        "速度": speed,
        "方向": direction,
        "海拔": altitude
    }
    # ===== 附加项解析 =====
    if ext_01_hex:
        # 智能判断输入格式：是否包含头部（0104）
        hex_str = ext_01_hex.strip().upper()
        if len(hex_str) == 12 and hex_str.startswith("0104"):
            # 格式1：完整附加项 "01040001B669"
            data_part_hex = hex_str[4:]  # 跳过 "0104"
        elif len(hex_str) == 8:
            # 格式2：仅数据部分 "0001B669"
            data_part_hex = hex_str
        else:
            raise ValueError(f"里程附加项格式错误: {ext_01_hex}。应为12位完整项或8位数据部分")
        mileage_raw = int(data_part_hex, 16)
        result["里程"] = mileage_raw

    if ext_03_hex:
        oil_or_speed = int(ext_03_hex, 16)
        result["附加项0x03"] = oil_or_speed
    if ext_25_hex:
        ext_value = int(ext_25_hex, 16)
        result["附加项0x25"] = ext_value

    return result

def replace_date_to_today(time_str: str = None) -> str:
    """
    如果传入时间字符串，则将其中的 年-月-日 替换为系统当前日期，
    时分秒保持不变。
    如果不传入参数，则返回当前系统时间。
    """
    # 若未传入参数，直接输出系统当前时间
    if not time_str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    possible_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y/%m/%d",
    ]

    dt = None
    fmt = None
    for f in possible_formats:
        try:
            dt = datetime.strptime(time_str, f)
            fmt = f
            break
        except:
            continue

    if dt is None:
        raise ValueError("无法识别时间格式，请检查输入")

    now = datetime.now()

    # 输入可能不含时分秒
    hour = getattr(dt, "hour", 0)
    minute = getattr(dt, "minute", 0)
    second = getattr(dt, "second", 0)

    # 替换日期为系统当天
    dt_new = datetime(now.year, now.month, now.day, hour, minute, second)

    return dt_new.strftime(fmt)

def random_adjust(number, max_change=10):
    """
    给整数随机加减一个值
    生成 -max_change 到 +max_change 之间的随机变化值
    """
    # 
    change = random.randint(-max_change, max_change)
    result = number + change
    return max(result, 0)  # 确保结果不小于0

def add_gps_noise(lat, lon, max_offset_meters=10):
    """
    为经纬度添加小范围随机偏移（模拟GPS噪声）
    
    参数:
    lat: 纬度
    lon: 经度
    max_offset_meters: 最大偏移距离（米），默认10米
    
    返回:
    (new_lat, new_lon): 偏移后的经纬度
    """
    # 地球半径（米）
    R = 6371000
    
    # 生成随机方向和距离
    # 随机角度（0到360度）
    angle = random.uniform(0, 2 * math.pi)
    # 随机距离（0到max_offset_meters）
    distance = random.uniform(0, max_offset_meters)
    
    # 将距离转换为弧度
    distance_rad = distance / R
    
    # 将角度转换为弧度
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    
    # 计算新的纬度
    new_lat_rad = math.asin(
        math.sin(lat_rad) * math.cos(distance_rad) + 
        math.cos(lat_rad) * math.sin(distance_rad) * math.cos(angle)
    )
    
    # 计算新的经度
    new_lon_rad = lon_rad + math.atan2(
        math.sin(angle) * math.sin(distance_rad) * math.cos(lat_rad),
        math.cos(distance_rad) - math.sin(lat_rad) * math.sin(new_lat_rad)
    )
    
    # 转换回度数
    new_lat = round(math.degrees(new_lat_rad), 6)
    new_lon = round(math.degrees(new_lon_rad), 6)
    
    return new_lat, new_lon

if __name__ == "__main__":
    hex_packet = """
    7E 02 00 00 2C 01 47 98 58 85 50 02 04 00 00 00 00 00 00 00 03 01 60 CC E5 06 BF AE FE 00 03 00 00 01 57 25 12 05 04 11 47 01 04 00 01 64 AC 03 02 00 00 25 04 00 00 00 00 7E
    """

    parsed = parse_gps_packet(hex_packet)
    # pretty_print(parsed)

    lat_hex = "01614264"
    lng_hex = "06C1A9D0"
    speed_hex = "0001"
    direction_hex = "0157"
    ext1 = "0104000164AC"
    ext2 = "03020000"
    ext3 = "250400000000"


    result = jt808_parse_location(lat_hex, lng_hex, speed_hex, direction_hex,ext1,ext2,ext3)
    # print(f"原数据 维度:{lat_hex} 经度:{lng_hex} 速度:{speed_hex} 方向:{direction_hex}")
    # print(result)

    # print(replace_date_to_today("2023-2-8 12:30:45"))

    result = random_adjust(0, 3)
    print(f"原始值:  0, 调整后: {result}")


    original_lat, original_lon = 23.165942, 113.359064
    new_lat, new_lon = add_gps_noise(original_lat, original_lon, max_offset_meters=15)
    # print(f"原始坐标: ({original_lat:.6f}, {original_lon:.6f})")
    # print(f"偏移后: ({new_lat}, {new_lon})")
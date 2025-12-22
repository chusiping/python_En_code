# jt808.py
import datetime
import testdate

def datetime_str_to_bcd_bytes(timestr: str) -> bytes:
    """
    将 "2025-11-14 00:01:39" 转为 6 字节 BCD bytes: YY MM DD hh mm ss
    返回 bytes(length=6)
    """
    dt = datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    parts = [
        dt.year % 100,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute,
        dt.second
    ]
    return bytes([(p // 10) << 4 | (p % 10) for p in parts])  # BCD: high nibble tens, low nibble units

def xor_checksum(data: bytes) -> bytes:
    cs = 0
    for b in data:
        cs ^= b
    return bytes([cs])

def escape_7e_7d(data: bytes) -> bytes:
    out = bytearray()
    for b in data:
        if b == 0x7E:
            out += b'\x7D\x02'
        elif b == 0x7D:
            out += b'\x7D\x01'
        else:
            out.append(b)
    return bytes(out)

def phone_to_bcd(phone: str) -> bytes:
    """
    将手机号字符串转为 BCD bytes（每个字节高4位十位，低4位个位）。
    若长度为奇数，左侧补 '0'（这样 "14798588550" -> "014798588550"）
    返回 bytes，例如: "14798588550" -> b'\x01\x47\x98\x58\x85\x50'
    """
    digits = ''.join(ch for ch in phone if ch.isdigit())
    if len(digits) % 2 != 0:
        digits = '0' + digits  # 左侧补0

    out = bytearray()
    for i in range(0, len(digits), 2):
        d1 = ord(digits[i]) - 48  # '0' -> 0
        d2 = ord(digits[i+1]) - 48
        if not (0 <= d1 <= 9 and 0 <= d2 <= 9):
            raise ValueError(f"invalid digit in phone: {digits[i:i+2]}")
        out.append((d1 << 4) | d2)
    return bytes(out)

def int_to_nbytes(v: int, n: int) -> bytes:
    return v.to_bytes(n, 'big', signed=False)

def build_0200(
    phone="14798588550",
    lat=0.0,
    lng=0.0,
    altitude=0,
    speed=0,
    direction=0,
    timestr="2025-12-04 16:43:17",
    mileage=0,
    msg_sn=0x0477,
    alarm=0,
    status=3,
    brake_on=True,          # 新增：刹车控制参数
    satellite_count=7       # 新增：卫星数量参数
) -> bytes:
    """
    构造 0200 报文并返回完整帧 bytes（已做 7E 转义并包含首尾 0x7E）
    """
    extended_signals = 0    
    if brake_on:
        # 如果要求刹车开，在原有status基础上添加BIT 17
        # status = status | (1 << 17)  # 设置BIT 17=1  这个设置无效且留下
        extended_signals |= (1 << 4)  # BIT 4 = 制动信号
    # 可以添加其他信号
        # if left_turn_on:   # 左转向灯
        #     extended_signals |= (1 << 3)
        # if right_turn_on:  # 右转向灯
        #     extended_signals |= (1 << 2)
        # if high_beam_on:   # 远光灯
        #     extended_signals |= (1 << 1)

    # ---- 时间（6 字节 BCD） ----
    time_bcd = datetime_str_to_bcd_bytes(timestr)
    assert isinstance(time_bcd, (bytes, bytearray)) and len(time_bcd) == 6, "time_bcd must be 6 bytes"

    # ---- 基本字段（全部 bytes） ----
    # alarm = b'\x00\x00\x00\x00'  # 报警标志 4 字节
    # status = b'\x00\x00\x00\x02'  # 状态 4 字节（示例：定位有效）
    alarm = int_to_nbytes(alarm, 4)    # 将 alarm 转成 4 字节
    status = int_to_nbytes(status, 4)  # 将 status 转成 4 字节
    lat_i = int(lat * 1_000_000) & 0xFFFFFFFF
    lng_i = int(lng * 1_000_000) & 0xFFFFFFFF
    lat_b = int_to_nbytes(lat_i, 4)
    lng_b = int_to_nbytes(lng_i, 4)
    altitude_b = int_to_nbytes(altitude & 0xFFFF, 2)
    speed_raw = int(speed * 10)  # 将实际速度转换为协议值
    speed_b = int_to_nbytes(speed_raw & 0xFFFF, 2)
    direction_b = int_to_nbytes(direction & 0xFFFF, 2)

    loc_body = alarm + status + lat_b + lng_b + altitude_b + speed_b + direction_b + time_bcd
    # check length of loc_body should be 28 for standard 0200
    assert len(loc_body) == 28, f"location body length expected 28, got {len(loc_body)}"

    # ---- 附加项（按你示例） ----
    # 0x01 里程，4 字节
    ext_01 = b'\x01\x04' + int_to_nbytes(mileage & 0xFFFFFFFF, 4)

    # 0x31 卫星数量（1字节，范围0-99）
    # 注意：卫星数量需要限制在有效范围
    sat_count = max(0, min(satellite_count, 99))  # 限制在0-99
    ext_31 = b'\x31\x01' + bytes([sat_count])

    # 0x03 示例（油量/速度类） 2 字节 value
    ext_03 = b'\x03\x02' + b'\x00\x00'
    # 0x25 扩展 4 字节
    # ext_25 = b'\x25\x04' + b'\x00\x00\x00\x00'
    ext_25 = b'\x25\x04' + int_to_nbytes(extended_signals & 0xFFFFFFFF, 4)
    ext_all = ext_01 + ext_03 + ext_25 + ext_31

    body = loc_body + ext_all

    # ---- 头部 ----
    msg_id = b'\x02\x00'
    body_len = len(body)  # 应该是 44 (0x2C) 如果附加项和示例一致
    header_no_escape = msg_id + int_to_nbytes(body_len, 2) + phone_to_bcd(phone) + int_to_nbytes(msg_sn & 0xFFFF, 2)

    # ---- 计算校验（对 header_no_escape + body）----
    checksum = xor_checksum(header_no_escape + body)

    # ---- 转义并加起止位 ----
    packet_no_frame = header_no_escape + body + checksum
    packet_escaped = escape_7e_7d(packet_no_frame)
    final = b'\x7E' + packet_escaped + b'\x7E'
    return final, packet_no_frame

# ================== 自测 ==================
if __name__ == "__main__":

    timestr = "2025-11-14 00:01:39"
    lat = 23.123456              #23.166388
    lng = 113.654321             #113.359064
    speed = 123                   # 速度 km/h
    direction = 456                # 方向 (度)
    altitude = 789                 # 海拔 (米)
    mileage = 112233

    pkt,raw = build_0200(
        phone="13305131386",
        lat=lat,
        lng=lng,
        altitude=altitude,
        speed=speed,
        direction=direction,
        timestr=timestr,
        mileage=mileage,
        msg_sn=0x0477
    )
    # 反向检查经纬度的7E7D
    # raw_hex = raw.hex().upper()
    # offset = (12 + 8) * 2
    # lat_hex = raw_hex[offset : offset + 8]          # 纬度 4 字节 = 8 hex 字符
    # lng_hex = raw_hex[offset + 8 : offset + 16]     # 经度 4 字节
    # print("LAT HEX =", lat_hex)
    # print("LNG HEX =", lng_hex)
    # lat = int(lat_hex, 16) / 1_000_000
    # lng = int(lng_hex, 16) / 1_000_000
    # print(lat, lng)
    # print(f"原据 维度:{lat} 经度:{lng} 速度:{speed} 方向:{direction}  ")

# 测试反解

    b_lat = pkt.hex().upper()[42:50]; 
    b_lng = pkt.hex().upper()[50:58]; 
    b_speed = pkt.hex().upper()[62:66]; 
    b_direction = pkt.hex().upper()[66:70]
    b_altitude = pkt.hex().upper()[58:62]
    b_mileage = pkt.hex().upper()[82:94]
    # print(f"\n维度\t{b_lat} \n经度\t{b_lng} \n速度\t{b_speed} \n方向\t{b_direction}  \n海拔\t{b_altitude}")
    # print(f"里程\t{b_mileage}")
    # print(f"\n")
    # print(testdate.jt808_parse_location(b_lat,b_lng,b_speed,b_direction,b_altitude,b_mileage))
    # print(f"\n")
    # print("HEX:", pkt.hex().upper())
    parsed = testdate.parse_gps_packet(pkt.hex().upper())
    testdate.pretty_print(parsed)   
    print(pkt)
    # 方便阅读按两位空格分隔
    # print("HEX spaced:", ' '.join(pkt.hex().upper()[i:i+2] for i in range(0, len(pkt.hex()), 2)))
    # print(int_to_nbytes(3,4))

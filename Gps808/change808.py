import struct
import time
from datetime import datetime
import readdate

def build_808_gps_message(plate_number, lat, lon, speed, direction, altitude, alarm=0, status=3):
    """
    构建808协议 0x0200 位置上报消息（使用车牌号）
    Args:
        plate_number: 车牌号码
        lat: 纬度 (浮点数)
        lon: 经度 (浮点数)
        speed: 速度 (km/h)
        direction: 方向 (0-359度)
        altitude: 海拔高度 (米)
        alarm: 报警标志 (默认0)
        status: 状态位 (默认3: ACC开+定位)
    """
    # 1. 消息ID - 位置信息汇报
    message_id = b'\x02\x00'
    
    # 2. 转换经纬度 (乘以10^6)
    lat_int = int(lat * 1000000)
    lon_int = int(lon * 1000000)
    
    # 3. 转换速度 (0.1km/h为单位)
    speed_int = int(speed * 10)
    
    # 4. 获取当前时间并转换为BCD码
    now = datetime.now()
    time_bcd = bytes([
        now.year % 100,  # 年-后两位
        now.month,       # 月
        now.day,         # 日
        now.hour,        # 时
        now.minute,      # 分
        now.second       # 秒
    ])
    
    # 5. 将车牌号转换为12位BCD码
    # 808协议要求12位BCD码，这里我们用车牌号的数字部分
    def plate_to_bcd(plate):
        """将车牌号转换为12位BCD码"""
        import re
        
        # 提取车牌中的所有数字
        numbers = re.findall(r'\d+', str(plate))
        if numbers:
            # 合并数字
            digits = ''.join(numbers)
            # 取前12位，不足补0
            if len(digits) >= 12:
                phone_str = digits[:12]
            else:
                phone_str = digits.zfill(12)
        else:
            # 如果没有数字，使用默认值
            phone_str = '123456789012'
        
        return bytes.fromhex(phone_str)
    
    phone_bcd = plate_to_bcd(plate_number)
    
    # 6. 构建消息体
    message_body = struct.pack('>IIiiHHH6s',
                               alarm & 0xFFFFFFFF,
                               status & 0xFFFFFFFF,
                               lat_int,
                               lon_int,
                               altitude & 0xFFFF,
                               speed_int & 0xFFFF,
                               direction & 0xFFFF,
                               time_bcd)
    
    # 7. 构建消息头
    body_length = len(message_body)
    msg_property = body_length & 0x3FFF
    msg_property_bytes = msg_property.to_bytes(2, 'big')
    
    # 消息流水号
    serial_num = int(time.time() * 1000) % 65536
    serial_bytes = serial_num.to_bytes(2, 'big')
    
    # 组装消息头
    message_header = message_id + msg_property_bytes + phone_bcd + serial_bytes
    
    # 8. 计算校验码
    check_code = 0
    for byte in message_header + message_body:
        check_code ^= byte
    
    # 9. 组装原始消息
    raw_message = message_header + message_body + bytes([check_code])
    
    # 10. 转义处理
    escaped = bytearray()
    for byte in raw_message:
        if byte == 0x7d:
            escaped.extend([0x7d, 0x01])
        elif byte == 0x7e:
            escaped.extend([0x7d, 0x02])
        else:
            escaped.append(byte)
    
    # 11. 添加起始和结束标志
    final_message = bytes([0x7e]) + bytes(escaped) + bytes([0x7e])
    
    return final_message

def print_packet_info(packet):
    """打印数据包信息"""
    print("\n" + "="*60)
    print("808协议数据包详细信息")
    
    # 1. 原始数据
    print("1. 完整数据包 (HEX):")
    hex_str = packet.hex().upper()
    for i in range(0, len(hex_str), 32):
        line = hex_str[i:i+32]
        # 每2个字符加一个空格
        formatted_line = ' '.join([line[j:j+2] for j in range(0, len(line), 2)])
        print(f"   {formatted_line}")
    
    # 2. 数据包长度
    print(f"\n2. 数据包总长度: {len(packet)} 字节")
    
    # 3. 解析消息结构
    print("\n3. 消息结构解析:")
    
    # 移除起始和结束符
    if packet[0] == 0x7e and packet[-1] == 0x7e:
        core_data = packet[1:-1]
        
        # 反转义处理
        unescaped = bytearray()
        i = 0
        while i < len(core_data):
            if core_data[i] == 0x7d and i + 1 < len(core_data):
                if core_data[i+1] == 0x01:
                    unescaped.append(0x7d)
                elif core_data[i+1] == 0x02:
                    unescaped.append(0x7e)
                i += 2
            else:
                unescaped.append(core_data[i])
                i += 1
        
        unescaped_bytes = bytes(unescaped)
        print(f"   - 反转义后数据: {unescaped_bytes.hex().upper()}")
        
        # 解析消息头
        if len(unescaped_bytes) >= 16:  # 消息头至少16字节
            print(f"\n4. 消息头解析:")
            print(f"   - 消息ID: 0x{unescaped_bytes[0:2].hex().upper()} (位置信息汇报)")
            
            # 消息体属性
            msg_property = int.from_bytes(unescaped_bytes[2:4], 'big')
            body_len = msg_property & 0x3FFF
            print(f"   - 消息体属性: 0x{unescaped_bytes[2:4].hex().upper()}")
            print(f"   - 消息体长度: {body_len} 字节")
            
            # 终端手机号
            phone_hex = unescaped_bytes[4:10].hex()
            print(f"   - 终端手机号: {phone_hex}")
            
            # 消息流水号
            serial = int.from_bytes(unescaped_bytes[10:12], 'big')
            print(f"   - 消息流水号: {serial}")
    

# ============ 使用示例 ============
if __name__ == "__main__":
    # 示例数据
    plate_number = "13305131386"  # 终端手机号
    latitude = 23.166388           # 纬度 (北京天安门)
    longitude = 113.359064         # 经度
    speed = 0                   # 速度 km/h
    direction = 348                # 方向 (度)
    altitude = 100                 # 海拔 (米)
    
    try:

        # 生成808协议数据包
        packet = build_808_gps_message(
            plate_number=plate_number,
            lat=latitude,
            lon=longitude,
            speed=speed,
            direction=direction,
            altitude=altitude
        )
        

        print_packet_info(packet)
        

        

    except Exception as e:
        print(f"\n未知错误: {type(e).__name__}: {e}")
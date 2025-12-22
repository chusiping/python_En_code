import datetime
import socket
import zhuanhuan

# 方法1：直接按BCD处理
def phone_to_bcd(phone_str: str) -> bytes:
    """手机号转6字节BCD"""
    if len(phone_str) != 11:
        raise ValueError("手机号必须是11位")
    
    # 确保手机号是纯数字
    phone_str = phone_str.strip()
    
    # 补0到12位（6字节=12个BCD码）
    padded = phone_str.rjust(12, '0')
    
    result = bytearray()
    for i in range(0, 12, 2):
        # 每两位数字转成一个字节
        high = int(padded[i])
        low = int(padded[i+1])
        result.append((high << 4) | low)
    
    return bytes(result)


def bcd_time(timestr: str) -> bytes:
    # dt_str format: "2025-11-14 00:01:39"
    import datetime

    dt = datetime.datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")

    # BCD = 字符串分段 → 每段直接转 hex
    bcd = (
        f"{dt.year % 100:02d}"   # YY
        f"{dt.month:02d}"        # MM
        f"{dt.day:02d}"          # DD
        f"{dt.hour:02d}"         # hh
        f"{dt.minute:02d}"       # mm
        f"{dt.second:02d}"       # ss
    )

    return bcd.upper()

def xor_checksum(data: bytes):
    cs = 0
    for b in data:
        cs ^= b
    return cs.to_bytes(1, 'big')

def escape_7e(data: bytes):
    """按 808 协议转义 7E、7D"""
    out = bytearray()
    for b in data:
        if b == 0x7E:
            out += b'\x7D\x02'
        elif b == 0x7D:
            out += b'\x7D\x01'
        else:
            out.append(b)
    return bytes(out)

def build_0200(
    phone="14798588550",
    lat=0.0,
    lng=0.0,
    altitude=0,
    speed=0,
    direction=0,
    dt=None,
    mileage=0
):
    if dt is None:
        dt = datetime.datetime.now()

    # 1. 消息头
    msg_id = b'\x02\x00'
    phone_bcd = phone_to_bcd(phone)
    msg_sn = b'\x04\x77'   # 随便写的流水号

    # 2. 位置信息体（标准 28 字节）
    alarm = b'\x00\x00\x00\x00'
    status = b'\x00\x00\x00\x02'     # 状态：bit1 = 定位有效
    lat_i = int(lat * 1_000_000).to_bytes(4, "big", signed=False)
    lng_i = int(lng * 1_000_000).to_bytes(4, "big", signed=False)
    altitude_b = altitude.to_bytes(2, "big")
    speed_b = speed.to_bytes(2, "big")
    direction_b = direction.to_bytes(2, "big")
    time_bcd = bcd_time(dt)

    loc_body = (
        alarm + status + lat_i + lng_i +
        altitude_b + speed_b + direction_b + time_bcd
    )

    # 3. 附加项（与您示例保持一致）
    # 里程 0x01
    ext_mileage = b'\x01\x04' + mileage.to_bytes(4, "big")

    # 油量/速度 0x03（示例写0）
    ext_03 = b'\x03\x02\x00\x00'

    # 扩展状态 0x25（示例写0）
    ext_25 = b'\x25\x04\x00\x00\x00\x00'

    ext_all = ext_mileage + ext_03 + ext_25

    # 全消息体
    body = loc_body + ext_all

    # 消息体长度
    msg_len = len(body).to_bytes(2, "big")

    header = msg_id + msg_len + phone_bcd + msg_sn

    # 校验
    cs = xor_checksum(header + body)

    # 拼成完整数据
    raw = b'\x7E' + escape_7e(header + body + cs) + b'\x7E'
    return raw.hex().upper()


def send_808_packet_tcp(packet_data, server_ip='14.23.86.188', server_port=6608):
    """
    使用TCP发送808协议数据包
    808协议通常使用TCP连接
    """
    sock = None
    try:
        # 创建TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)  # 设置超时时间
        
        print(f"  连接到 {server_ip}:{server_port}...")
        sock.connect((server_ip, server_port))
        print("  ✓ 连接成功!")
        
        print(f"  发送数据包 ({len(packet_data)} 字节)...")
        sock.sendall(packet_data)
        print("  ✓ 发送成功!")
        
        # 接收服务器响应
        print("  等待响应...")
        response = sock.recv(1024)
        
        if response:
            print(f"  ✓ 收到响应 ({len(response)} 字节):")
            print(f"    HEX: {response.hex().upper()[:80]}...")
            print(f"    明文: {zhuanhuan.parse_808_response(response)}")

        else:
            print("  ⓘ 收到空响应")
            
        return True, response
        
    except socket.timeout:
        print("  ✗ 连接或接收超时")
        return False, None
    except ConnectionRefusedError:
        print("  ✗ 连接被拒绝，服务器可能未启动")
        return False, None
    except Exception as e:
        print(f"  ✗ 错误: {type(e).__name__}: {e}")
        return False, None
    finally:
        if sock:
            try:
                sock.close()
            except:
                pass




if __name__ == "__main__":
    print("Running JT808 0200 Builder self-test...\n")

    packet = build_0200(
        phone="13305131386",
        lat=23.166388,                                  # 举例：你的包里面的“异常纬度”
        lng=113.359064,                                         # 你的经度
        altitude=0,
        speed=0,
        direction=0,
        dt='2025-11-14 00:01:39'
        # mileage=90760                                              #  取消就成功了
    )

    print("生成的报文：")
    print(packet)
    print("\n长度：", len(packet))

    SERVER_IP = '14.23.86.188'
    SERVER_PORT = 6608
    SEND_TO_SERVER = True  # 是否发送到服务器
    
    print("=" * 60)
    print("808协议数据包生成与TCP发送系统")

    if SEND_TO_SERVER:
        print(f"\n[发送到服务器]")
        packet_bytes = bytes.fromhex(packet)
        success, response = send_808_packet_tcp(packet_bytes, SERVER_IP, SERVER_PORT)
        
        if success:
            print(f"处理完成")
        else:
            print(f"记录发送失败")
    else:
        print(f"\nⓘ 演示模式: 跳过发送")
        print(f"  数据包HEX: {packet.hex().upper()[:60]}...")
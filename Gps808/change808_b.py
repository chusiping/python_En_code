import struct
import time
from datetime import datetime
import crcmod

class JTT808Converter:
    def __init__(self, phone_number="12345678901"):
        # 终端手机号 (BCD码, 12位)
        self.phone_number = phone_number.ljust(12, 'F')
        self.msg_serial = 0
        
    def calculate_bcc(self, data):
        """异或校验"""
        checksum = 0
        for byte in data:
            checksum ^= byte
        return checksum
    
    def escape_data(self, data):
        """转义处理 (0x7E -> 0x7D 0x02, 0x7D -> 0x7D 0x01)"""
        escaped = bytearray()
        for byte in data:
            if byte == 0x7E:
                escaped.extend([0x7D, 0x02])
            elif byte == 0x7D:
                escaped.extend([0x7D, 0x01])
            else:
                escaped.append(byte)
        return escaped
    
    def create_position_message(self, vehicle_data):
        """
        创建位置信息汇报消息 (0x0200)
        
        vehicle_data 格式示例:
        {
            "plate": "粤AFN728",
            "time": "2025-11-14 00:01:39",
            "alarm": 0,  # 报警标志
            "status": 0, # 状态位
            "lon": 113.359064,
            "lat": 23.166388,
            "altitude": 0,
            "speed": 34.8,  # km/h
            "direction": 348,  # 0-359度
            "acc": True,    # ACC状态
            "brake": True,  # 刹车
            "left_light": True,  # 左转向灯
            "high_beam": True,   # 远光灯
            "mileage": 17716,  # 里程
        }
        """
        # 1. 消息头
        msg_id = 0x0200  # 位置汇报
        
        # 消息体属性
        msg_body_attr = 0x0028  # 0010 1000: 版本2011，有附加信息，消息体长度待定
        
        # 终端手机号 (BCD码)
        phone_bcd = bytes.fromhex(self.phone_number)
        
        # 消息流水号
        self.msg_serial = (self.msg_serial + 1) & 0xFFFF
        
        # 2. 消息体 - 位置基本信息
        # 报警标志 (DWORD)
        alarm_flag = vehicle_data.get('alarm', 0)
        
        # 状态位 (DWORD)
        status = 0
        if vehicle_data.get('acc', False):
            status |= 0x00000100  # ACC开
        if vehicle_data.get('brake', False):
            status |= 0x00080000  # 刹车
        if vehicle_data.get('left_light', False):
            status |= 0x00000010  # 左转向灯
        if vehicle_data.get('high_beam', False):
            status |= 0x00000040  # 远光灯开
        
        # 经度 (DWORD, 1/10^6 度)
        lon = int(vehicle_data['lon'] * 1000000)
        
        # 纬度 (DWORD, 1/10^6 度)
        lat = int(vehicle_data['lat'] * 1000000)
        
        # 高程 (WORD, 米)
        altitude = vehicle_data.get('altitude', 0)
        
        # 速度 (WORD, 1/10 km/h)
        speed = int(vehicle_data.get('speed', 0) * 10)
        
        # 方向 (WORD, 0-359)
        direction = vehicle_data.get('direction', 0)
        
        # 时间 (BCD[6], YY-MM-DD-hh-mm-ss)
        time_str = vehicle_data['time']
        dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        time_bcd = bytes([
            dt.year % 100, dt.month, dt.day,
            dt.hour, dt.minute, dt.second
        ])
        
        # 3. 附加信息
        extras = bytearray()
        
        # 里程 (附加信息ID: 0x01, 长度: 4)
        mileage = vehicle_data.get('mileage', 0)
        if mileage > 0:
            extras.append(0x01)  # ID
            extras.append(0x04)  # 长度
            extras.extend(struct.pack('>I', int(mileage * 10)))  # 1/10公里
        
        # 视频丢失报警 (附加信息ID: 0x14, 长度: 1+n)
        # 通道21视频丢失
        video_alarm = vehicle_data.get('video_lost', [])
        if 21 in video_alarm:
            extras.append(0x14)  # ID
            channel_count = 1
            extras.append(1 + channel_count)  # 长度
            extras.append(0x01)  # 丢失类型
            extras.append(21)    # 通道号
        
        # 停车时间 (附加信息ID: 0x20, 长度: 2)
        # 停车22小时20分 = 1340分钟
        parking_minutes = vehicle_data.get('parking_minutes', 0)
        if parking_minutes > 0:
            extras.append(0x20)  # ID
            extras.append(0x02)  # 长度
            extras.extend(struct.pack('>H', parking_minutes))
        
        # 4. 构建完整消息体
        msg_body = struct.pack(
            '>IIIIHHH6s',
            alarm_flag,
            status,
            lon,
            lat,
            altitude & 0xFFFF,
            speed & 0xFFFF,
            direction & 0xFFFF,
            time_bcd
        )
        
        msg_body = bytearray(msg_body)
        msg_body.extend(extras)
        
        # 5. 消息体属性设置长度
        msg_body_attr |= (len(msg_body) & 0x3FF)
        
        # 6. 构建完整消息
        header = struct.pack(
            '>HH12sH',
            msg_id,
            msg_body_attr,
            phone_bcd,
            self.msg_serial
        )
        
        msg_without_check = header + msg_body
        
        # 7. 计算校验码
        checksum = self.calculate_bcc(msg_without_check)
        
        # 8. 构建完整包
        full_msg = b'\x7e' + msg_without_check + bytes([checksum]) + b'\x7e'
        
        # 9. 转义处理
        escaped_msg = self.escape_data(full_msg)
        
        return escaped_msg
    
    def parse_position_data(self, raw_data):
        """将你的原始文本数据解析为结构化数据"""
        # 解析示例: 粤AFN728	是	2025-11-14 00:01:39	0	113.359064	23.166388	348...
        parts = raw_data
        
        data = {
            'plate': parts[0],
            'time': parts[2],
            'alarm': 0,
            'lon': float(parts[4]), #经度
            'lat': float(parts[5]),
            'direction': int(parts[6]),
            'acc': 'ACC开' in parts[8] ,
            'brake': '刹车' in parts[8],
            'left_light': '左转向灯开' in parts[8],
            'high_beam': '远光灯开' in parts[8],
            'address': parts[7]
        }
        
        # 解析里程
        if '里程：' in parts[8]:
            mileage_part = parts[8].split(';')[0].split('：')[1].split('km')[0]
            data['mileage'] = float(mileage_part)
        
        # 解析速度 (如果有单独的速度字段)
        try:
            data['speed'] = float(parts[3])
        except:
            data['speed'] = 0
        
        return data


# 使用示例
def main():
    converter = JTT808Converter(phone_number="13305131386")
    
    # 你的原始数据
    raw_data = ['粤AFN728','是','2025-11-14 00:01:39','141','113.359064','23.166388','348','广东省广州市天河区五山街道S4华南快速同挥驾校','里程：17716km;ACC开、视频丢失:通道21、停车22小时20分、刹车、左转向灯开、远光灯开']

    
    # 1. 解析数据
    vehicle_data = converter.parse_position_data(raw_data)
    print("解析后的数据:")
    for key, value in vehicle_data.items():
        print(f"  {key}: {value}")
    
    # 2. 生成JTT808协议包
    jtt808_packet = converter.create_position_message(vehicle_data)
    
    print(f"\n生成的JTT808数据包 ({len(jtt808_packet)} 字节):")
    print(f"HEX: {jtt808_packet.hex().upper()}")
    
    # 3. 保存到文件
    with open('gps_data.jtt808', 'wb') as f:
        f.write(jtt808_packet)
    
    # 4. 解析验证
    print("\n包结构解析:")
    print(f"起始符: 0x{jtt808_packet[0]:02X}")
    print(f"消息ID: 0x{jtt808_packet[1:3].hex().upper()}")
    print(f"消息体属性: 0x{jtt808_packet[3:5].hex().upper()}")
    print(f"终端手机号: {jtt808_packet[5:17].hex()}")
    print(f"消息流水号: {int.from_bytes(jtt808_packet[17:19], 'big')}")
    
    return jtt808_packet


if __name__ == "__main__":
    packet = main()
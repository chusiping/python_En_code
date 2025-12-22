import struct

def parse_808_response(response_data):
    """
    解析808协议响应数据
    参数: response_data - 字节类型的响应数据
    返回: 解析后的字典
    """
    if not response_data:
        return {"error": "空响应"}
    
    print(f"\n[808协议响应解析]")
    print(f"原始数据 ({len(response_data)} 字节): {response_data.hex().upper()}")
    
    try:
        # 检查起始和结束标志
        if response_data[0] != 0x7e or response_data[-1] != 0x7e:
            print("警告: 响应数据格式不标准，可能不是完整的808协议包")
        
        # 1. 去除起始和结束标志 (0x7e)
        core_data = response_data[1:-1]
        
        # 2. 反转义处理
        unescaped = bytearray()
        i = 0
        while i < len(core_data):
            if core_data[i] == 0x7d and i + 1 < len(core_data):
                if core_data[i+1] == 0x01:
                    unescaped.append(0x7d)
                elif core_data[i+1] == 0x02:
                    unescaped.append(0x7e)
                else:
                    unescaped.append(core_data[i])  # 未知转义，保留原样
                i += 2
            else:
                unescaped.append(core_data[i])
                i += 1
        
        unescaped_bytes = bytes(unescaped)
        print(f"反转义后: {unescaped_bytes.hex().upper()}")
        
        # 3. 解析消息头 (至少12字节)
        if len(unescaped_bytes) < 12:
            return {"error": "响应数据太短", "hex": response_data.hex().upper()}
        
        # 消息ID (2字节)
        message_id = unescaped_bytes[0:2]
        msg_id_hex = message_id.hex().upper()
        
        # 消息体属性 (2字节)
        msg_property = int.from_bytes(unescaped_bytes[2:4], 'big')
        body_length = msg_property & 0x3FFF  # 低14位为消息体长度
        
        # 终端手机号 (6字节BCD码)
        phone_bcd = unescaped_bytes[4:10]
        phone_hex = phone_bcd.hex()
        
        # 消息流水号 (2字节)
        serial_num = int.from_bytes(unescaped_bytes[10:12], 'big')
        
        # 校验码 (1字节，在消息体之后)
        if len(unescaped_bytes) > 12 + body_length:
            check_code = unescaped_bytes[12 + body_length]
        else:
            check_code = None
        
        result = {
            "message_id": msg_id_hex,
            "message_id_desc": get_message_id_desc(msg_id_hex),
            "body_length": body_length,
            "phone": phone_hex,
            "serial_number": serial_num,
            "check_code": check_code,
            "raw_hex": response_data.hex().upper()
        }
        
        # 4. 解析消息体
        if body_length > 0 and len(unescaped_bytes) >= 12 + body_length:
            message_body = unescaped_bytes[12:12 + body_length]
            result["body_hex"] = message_body.hex().upper()
            
            # 根据消息ID解析消息体
            if msg_id_hex == "8001":  # 平台通用应答
                result.update(parse_8001_response(message_body))
            elif msg_id_hex == "8100":  # 终端注册应答
                result.update(parse_8100_response(message_body))
            else:
                result["body_desc"] = f"未知消息体类型: {msg_id_hex}"
        
        return result
        
    except Exception as e:
        return {
            "error": f"解析失败: {str(e)}",
            "raw_hex": response_data.hex().upper()
        }

def get_message_id_desc(message_id_hex):
    """获取消息ID描述"""
    msg_id_map = {
        "0001": "终端心跳",
        "0002": "终端注销",
        "0100": "终端注册",
        "0102": "终端鉴权",
        "0200": "位置信息汇报",
        "0201": "位置信息查询",
        "0800": "多媒体事件信息上传",
        "0801": "多媒体数据上传",
        "0802": "存储多媒体数据检索",
        "0805": "摄像头立即拍摄命令",
        "8001": "平台通用应答",
        "8100": "终端注册应答",
        "8103": "设置终端参数",
        "8104": "查询终端参数应答",
        "8105": "终端控制",
        "8106": "查询指定终端参数",
        "8107": "查询终端属性",
        "8108": "下发终端升级包",
        "8201": "位置信息查询应答",
        "8202": "临时位置跟踪控制",
        "8203": "人工确认报警消息",
        "8300": "文本信息下发",
        "8301": "事件设置",
        "8302": "提问下发",
        "8303": "信息点播菜单设置",
        "8304": "信息服务",
        "8400": "电话回拨",
        "8401": "设置电话本",
        "8500": "车辆控制",
        "8600": "设置圆形区域",
        "8601": "删除圆形区域",
        "8602": "设置矩形区域",
        "8603": "删除矩形区域",
        "8604": "设置多边形区域",
        "8605": "删除多边形区域",
        "8606": "设置路线",
        "8607": "删除路线",
        "8700": "行驶记录仪数据采集命令",
        "8701": "行驶记录仪数据上传",
        "8702": "行驶记录仪参数下传命令",
        "8800": "多媒体数据上传应答",
        "8801": "摄像头立即拍摄命令应答",
        "8802": "存储多媒体数据检索应答",
        "8900": "数据下行透传",
        "8A00": "平台RSA公钥",
        "8B00": "终端RSA公钥",
    }
    return msg_id_map.get(message_id_hex.upper(), "未知消息")

def parse_8001_response(body_data):
    """解析平台通用应答 (0x8001)"""
    result = {}
    try:
        if len(body_data) >= 5:
            # 应答流水号 (2字节)
            serial_num = int.from_bytes(body_data[0:2], 'big')
            result["response_serial"] = serial_num
            
            # 应答消息ID (2字节)
            response_msg_id = body_data[2:4].hex().upper()
            result["response_to_message"] = response_msg_id
            
            # 结果 (1字节)
            result_code = body_data[4]
            result["result"] = result_code
            result["result_desc"] = {
                0: "成功/确认",
                1: "失败",
                2: "消息有误",
                3: "不支持",
            }.get(result_code, f"未知({result_code})")
    except:
        pass
    return result

def parse_8100_response(body_data):
    """解析终端注册应答 (0x8100)"""
    result = {}
    try:
        if len(body_data) >= 3:
            # 应答流水号 (2字节)
            serial_num = int.from_bytes(body_data[0:2], 'big')
            result["response_serial"] = serial_num
            
            # 结果 (1字节)
            result_code = body_data[2]
            result["result"] = result_code
            result["result_desc"] = {
                0: "成功",
                1: "车辆已被注册",
                2: "数据库中无该车辆",
                3: "终端已被注册",
                4: "数据库中无该终端",
            }.get(result_code, f"未知({result_code})")
            
            # 鉴权码 (如果有)
            if len(body_data) > 3 and result_code == 0:
                auth_code = body_data[3:].decode('ascii', errors='ignore')
                result["auth_code"] = auth_code
    except:
        pass
    return result


if __name__ == "__main__":
    parse_808_response()
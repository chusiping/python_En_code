import socket
import threading
from parser import parse_jt808_packet
from parser_factory import *
from protocol_load import load_protocol_config
from save_result import * 
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import base64
import hashlib

import sys

# TCP收到设备数据 → 判断协议 → 找解析器 → 解析 → 转明文 → 保存
"""
    1 server_interface.py
        protocol = ProtocolDetector.detect(data)  协议识别
        ParserFactory.get(protocol)
    3 
""" 

PROTOCOL_MAP = load_protocol_config()
detector = ProtocolDetector(PROTOCOL_MAP)

HOST = "0.0.0.0"
PORT = 7534

def get_current_hour_logger():
    """动态获取或更新当前小时的日志 Handler，并存放在 log 文件夹下"""
    # 1. 确保当前目录下存在名为 'log' 的文件夹
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # 2. 拼接路径，生成如 'log/2026080917.log' 的完整路径
    current_hour = datetime.datetime.now().strftime("%Y_%m_%d_%H")
    log_filename = f"{current_hour}.log"
    full_log_path = os.path.join(log_dir, log_filename)
    
    # 3. 获取名为 "device_server" 的日志记录器通道
    local_logger = logging.getLogger("device_server")
    local_logger.setLevel(logging.INFO)
    
    # 检查是否已经配置了当前小时的文件 Handler
    has_file_handler = False
    
    # 检查现有的处理器，如果不是当前小时的文件，就移除并关闭它
    for h in local_logger.handlers[:]:
        if isinstance(h, logging.FileHandler):
            # 如果绑定的文件名就是我们现在要的文件名，说明不需要重复添加
            if os.path.abspath(h.baseFilename) == os.path.abspath(full_log_path):
                has_file_handler = True
            else:
                local_logger.removeHandler(h)
                h.close()
                
    # 如果还没有添加控制台（屏幕）打印输出，则添加
    if not any(isinstance(h, logging.StreamHandler) for h in local_logger.handlers):
        sh = logging.StreamHandler()
        sh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        local_logger.addHandler(sh)
        
    # 如果没有当前小时的文件处理器，则新建一个
    if not has_file_handler:
        fh = logging.FileHandler(full_log_path, encoding="utf-8")
        fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        local_logger.addHandler(fh)
        
    return local_logger

def recv_all_hex(data):
    return data.hex().upper()
def client_thread(conn, addr):
    log = get_current_hour_logger()

    log.info(" ")
    log.info(f"设备连接：{addr}")
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            
            # 每次收到新数据，刷新 logger 以防时间跨到了下一个小时
            log = get_current_hour_logger()
            
            hexstr = recv_all_hex(data)
            log.info(f"收到数据: {hexstr}")
            
            try:
                # 1. 协议识别
                protocol = detector.detect(data)
                log.info(f"识别协议: {protocol}")
                
                # 2. 获取解析器
                parser = ParserFactory.get(protocol)
                if parser:
                    # 3. 解析
                    result = parser.parse(data)
                    filename = save_result(result)
                    log.info(f"保存: {filename}")
                    log.info("解析结果:")
                    for k, v in result.items():
                        log.info(f"{k:<20}: {v}")
                else:
                    log.warning("没有对应解析器")
            except Exception as e:
                log.error(f"解析失败: {e}", exc_info=True)
    finally:
        conn.close()
        log = get_current_hour_logger()
        log.info(f"已断开!!!")

def check_expire():
    """动态校验外部的 license.lic 文件"""
    SECRET_KEY = "K9#mX!2pQ$zL7vW@eR9t" # 必须与生成器完全一致
    lic_file = "license.lic"
    
    # 1. 检查证书文件是否存在
    if not os.path.exists(lic_file):
        print("=" * 80)
        print("❌ 错误：未找到授权证书文件 (license.lic)！程序无法启动。")
        print("=" * 80)
        sys.exit(1)
        
    try:
        # 2. 读取并解码 Base64
        with open(lic_file, "r", encoding="utf-8") as f:
            encoded_content = f.read().strip()
        
        decoded_content = base64.b64decode(encoded_content.encode('utf-8')).decode('utf-8')
        expire_str, client_sign = decoded_content.split("|")
        
        # 3. 重新计算签名，验证文件是否被客户篡改过
        raw_data = f"{expire_str}|{SECRET_KEY}"
        expected_sign = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
        
        if client_sign != expected_sign:
            print("❌ 错误：授权证书签名无效！")
            sys.exit(1)
            
        # 4. 比较时间是否过期
        expire_date = datetime.strptime(expire_str, "%Y-%m-%d")
        if datetime.now() > expire_date:
            print("=" * 80)
            print(f"❌ 错误：授权证书已于 {expire_str} 结束！请联系开发人员获取新证书。")
            print("=" * 80)
            sys.exit(1)
            
        print(f"✅ 证书通过!")
        
    except Exception as e:
        print(f"❌ 错误：解析授权证书失败！原因: {e}")
        sys.exit(1)

def start_server():
    check_expire()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(20)
    print("=" * 80)
    print("JT808测试服务器启动")
    print(f"监听：{HOST}:{PORT}")
    print("=" * 80)
    while True:
        conn, addr = server.accept()
        threading.Thread(
            target=client_thread,
            args=(conn, addr),
            daemon=True
        ).start()

if __name__ == "__main__":
    start_server()


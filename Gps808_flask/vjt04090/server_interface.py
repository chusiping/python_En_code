import socket
import threading
from parser import parse_jt808_packet
from protocol_detector import ProtocolDetector
from parser_factory import *
from protocol_load import load_protocol_config

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

def recv_all_hex(data):
    return data.hex().upper()
def client_thread(conn, addr):
    print("=" * 80)
    print(f"设备连接：{addr}")
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            hexstr = recv_all_hex(data)
            print("\n收到数据：")
            print(hexstr)
            try:
                # 1. 协议识别
                protocol = detector.detect(data)
                print(
                    "识别协议:",
                    protocol
                )
                # 2. 获取解析器
                parser = ParserFactory.get(protocol)  # 根据协议选择函数
                if parser:
                    # 3. 解析
                    result = parser.parse(data)
                    print("解析结果:")
                    for k,v in result.items():
                        print(
                            f"{k:<20}: {v}"
                        )
                else:
                    print(
                        "没有对应解析器"
                    )
            except Exception as e:
                print(
                    "解析失败:",
                    e
                )
    finally:
        conn.close()
        print(
            f"{addr} 已断开"
        )

def start_server():
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


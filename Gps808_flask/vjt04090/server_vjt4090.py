import socket
import threading
from parser import parse_jt808_packet

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
            print("-" * 80)
            try:
                result = parse_jt808_packet(hexstr)
                print("解析结果：")
                if isinstance(result, dict):
                    for k, v in result.items():
                        print(f"{k:<20}: {v}")
                else:
                    print(result)
            except Exception as e:
                print("解析失败：", e)

    finally:
        conn.close()
        print(f"{addr} 已断开")

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
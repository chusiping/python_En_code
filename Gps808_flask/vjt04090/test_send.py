import socket
host = "127.0.0.1"
# host = "14.23.86.188"
port = 7534
hexstr = ""
data = bytes.fromhex(hexstr)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))
sock.send(data)
sock.close()
# 去重后
# 7E0002	0002	心跳
# 7E0200	0200	位置信息汇报
# 7E0205	0205	位置查询应答
# 7E0510	0510	终端链路检测请求（JT808）
# 7E0900	0900	数据上行透传
# 7E8001	8001	平台通用应答
# 7E2002	2002	人工确认报警消息
# 7EA8C0	A8C0	（异常/扩展ID，需要看上下文）
# 7EC06B	C06B	（异常/扩展ID，需要看上下文）
# 7E7E80	7E80	异常，疑似转义未还原
# 7E7E02	7E02	异常，疑似转义未还原

# 测试三台车
# 18761241944(洒水车的)
# 18761241943(压缩车)
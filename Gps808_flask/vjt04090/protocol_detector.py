# class ProtocolDetector:
#     JT808_MSG = [
#         0x0001,
#         0x8001,
#         0x0200,
#         0x0704,
#         0x0900
#     ]
#     def detect(data):
#         if data[0] == 0x7E:
#             msg_id = data[1:3]
#             if msg_id in JT808_MSG:
#                 return "JT808"
#             if msg_id in VJT_MSG:
#                 return "VJT"
#         return "UNKNOWN"
    

class ProtocolDetector:
    def __init__(self, protocol_map):
        self.protocol_map = protocol_map
    def detect(self, data):
        if not data:
            return "UNKNOWN"
        # 判断7E
        if data[0] != 0x7E:
            return "UNKNOWN"
        # 消息ID
        msg_id = data[1:3].hex().upper()
        for protocol, msg_list in self.protocol_map.items():
            if msg_id in msg_list:
                return protocol
        return "UNKNOWN"

# # 主入口非常简单最终你的接口：
# def receive(data):
#     protocol = ProtocolDetector.detect(data)
#     parser = ParserFactory.get(protocol)
#     result = parser.parse(data)
#     save_raw(data)
#     save_result(result)


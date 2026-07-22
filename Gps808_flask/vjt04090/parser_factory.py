from parser import * 

class JT808Parser:
    def parse(self,data):
        hexstr=data.hex().upper()
        return parse_jt808_packet(hexstr)
    
class VJTParser:
    def parse(self,data):
        hexstr=data.hex().upper()
        return parse_0900(hexstr)
    
class ParserFactory:
    parsers = {
        "JT808":JT808Parser(),
        "VJT":VJTParser()
    }
    @staticmethod
    def get(protocol):
        return ParserFactory.parsers.get(protocol)
    
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
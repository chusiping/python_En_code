# 包装 parse_jt808_packet
from parser import * 
class JT808Parser:
    def parse(self,data):
        hexstr=data.hex().upper()
        return parse_jt808_packet(hexstr)
    
class VJTParser:
    def parse(self,data):
        hexstr=data.hex().upper()
        return parse_0900(hexstr)

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
    
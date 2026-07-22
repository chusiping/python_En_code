from JT808Parser import *
class ParserFactory:
    parsers = {
        "JT808":JT808Parser(),
        "VJT":VJTParser()
    }
    @staticmethod
    def get(protocol):
        return ParserFactory.parsers.get(protocol)
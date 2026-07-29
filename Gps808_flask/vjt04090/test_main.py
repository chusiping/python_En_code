from transparent import build_0900
from parser import parse_jt808_packet
from save_result import *
if __name__ == "__main__":
    result = parse_jt808_packet("7E0002000001876124194383B4AC7E")
    # print(f0200_1)
    # print(result)
    import json
    json_file = save_result(result)
    os.startfile(json_file)


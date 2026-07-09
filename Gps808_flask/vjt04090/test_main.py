from transparent import build_0900
from parser import parse_jt808_packet


if __name__ == "__main__":

    # packet = build_0900(
    #     phone="13305131386",
    #     msg_sn=1,
    #     function_id=0xF2,
    #     data=b'\x01\x02\x03'
    # )

    # print(packet.hex(" ").upper())


    hex_packet = """
7E 09 00 00 07 01 87 61 24 19 44 2A 8C F3 26 07 09 17 08 55 A7 7E
"""


    result = parse_jt808_packet(hex_packet)
    print(result)



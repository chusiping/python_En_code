# 公共编码
# codec.py

def xor_checksum(data: bytes) -> bytes:
    cs = 0
    for b in data:
        cs ^= b
    return bytes([cs])


def escape_7e_7d(data: bytes) -> bytes:
    out = bytearray()

    for b in data:
        if b == 0x7E:
            out += b'\x7D\x02'
        elif b == 0x7D:
            out += b'\x7D\x01'
        else:
            out.append(b)

    return bytes(out)


def int_to_nbytes(v:int, n:int):
    return v.to_bytes(n, 'big')


def phone_to_bcd(phone:str):

    digits = ''.join(
        c for c in phone if c.isdigit()
    )

    if len(digits)%2:
        digits='0'+digits

    result=bytearray()

    for i in range(0,len(digits),2):

        result.append(
            ((ord(digits[i])-48)<<4)
            |
            (ord(digits[i+1])-48)
        )

    return bytes(result)

def split_hex(hexstr):
    """
    JT/T808 解转义
    输入: 十六进制字符串
    例如: 02007D027D01AB
    输出:
    02007E7DAB
    """
    hexstr = hexstr.upper().replace(" ", "").replace("\n", "")
    result = []
    idx = 0

    while idx < len(hexstr):

        # 判断是否遇到7D
        if hexstr[idx:idx+2] == "7D":

            # 防止越界
            if idx + 4 > len(hexstr):
                raise ValueError("转义码不完整")

            next_byte = hexstr[idx+2:idx+4]

            if next_byte == "01":
                # 7D01 -> 7D
                result.append("7D")

            elif next_byte == "02":
                # 7D02 -> 7E
                result.append("7E")

            else:
                # 非法转义
                raise ValueError(
                    f"非法转义: 7D{next_byte}"
                )

            idx += 4

        else:
            result.append(hexstr[idx:idx+2])
            idx += 2

    return "".join(result)

def parse_bcd_time(hexstr):
    """
    解析 JT808/VJT BCD[6] 时间

    格式:
    YY MM DD HH MM SS

    例如:
    260709154649

    返回:
    2026-07-09 15:46:49
    """

    if len(hexstr) != 12:
        raise ValueError(
            f"BCD时间长度错误: {hexstr}"
        )

    yy = int(hexstr[0:2])
    mm = int(hexstr[2:4])
    dd = int(hexstr[4:6])

    hh = int(hexstr[6:8])
    mi = int(hexstr[8:10])
    ss = int(hexstr[10:12])


    return (
        f"20{yy:02d}-"
        f"{mm:02d}-"
        f"{dd:02d} "
        f"{hh:02d}:"
        f"{mi:02d}:"
        f"{ss:02d}"
    )

def parse_u32(hexstr):
    return int(hexstr,16)


def parse_u16(hexstr):
    return int(hexstr,16)


def parse_lat(hexstr):

    value = int(hexstr,16)

    # Bit31方向
    south = value & 0x80000000

    value &= 0x7FFFFFFF

    lat = value / 1000000

    if south:
        lat = -lat

    return lat



def parse_lng(hexstr):

    value = int(hexstr,16)

    west = value & 0x80000000

    value &= 0x7FFFFFFF

    lng=value/1000000

    if west:
        lng=-lng

    return lng
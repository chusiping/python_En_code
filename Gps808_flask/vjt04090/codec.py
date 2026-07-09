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
    hexstr = hexstr.replace(" ", "").replace("\n", "")
    return hexstr.upper()
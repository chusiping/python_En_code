# 0200
from message import build_packet
def build_0200(
        phone,
        msg_sn,
        body
):

    return build_packet(
        b'\x02\x00',
        phone,
        msg_sn,
        body
    )
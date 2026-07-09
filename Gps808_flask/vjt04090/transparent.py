# 0900 上行透传
from message import build_packet
def build_0900(
        phone,
        msg_sn,
        function_id,
        data:bytes
):

    body = (
        bytes([function_id])
        +
        data
    )


    return build_packet(
        b'\x09\x00',
        phone,
        msg_sn,
        body
    )

# 例如车辆故障：
# pkt = build_0900(
#     phone="13305131386",
#     msg_sn=1,
#     function_id=0xF2,
#     data=b'\x01\x02'
# )
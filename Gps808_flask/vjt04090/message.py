# message.py

from codec import *


def build_packet(
        msg_id:bytes,
        phone:str,
        msg_sn:int,
        body:bytes
):

    header = (
        msg_id
        +
        int_to_nbytes(len(body),2)
        +
        phone_to_bcd(phone)
        +
        int_to_nbytes(msg_sn,2)
    )


    check = xor_checksum(
        header+body
    )


    raw = (
        header
        +
        body
        +
        check
    )


    return (
        b'\x7E'
        +
        escape_7e_7d(raw)
        +
        b'\x7E'
    )
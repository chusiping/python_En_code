s = "0200" 
b = bytes.fromhex(s) 
n = int.from_bytes(b, "big")
xn = int.from_bytes(b, "little")
n2 = int.from_bytes(bytes.fromhex("0200"), "big")


print(f'两个十六进制字节: s={s}')
print(f'bytes.fromhex(s)  转成字节数据: b={b}')
print(f'int.from_bytes(b, "big") 大端转整数: n={n}')
print(f'int.from_bytes(b, "little") 小端转整数: xn={xn}')
print(f'int.from_bytes直接转转整数: n={n}')

info = f"""
1   JT808 收到的数据通常不是字符串
    TCP 收到：7E 02 00 00 05 01 87
    socket 得到：data = b'\x7e\x02\x00\x00\x05\x01\x87' 这是 bytes

    取消息ID： msg_id_bytes = data[1:3] 得到 b'\x02\x00'

    如果你手工：hexstr = "7E0200000501876124194400062B"
    msg_id = int(hexstr[2:6],16)
    得到：512

    但是实际程序：
    data = bytes.fromhex(hexstr)
    msg_id = int.from_bytes(data[1:3],"big")
    更合理

    hexstr = "7E0200000501876124194400062B" 
    和 
    hexstr = "7E 02 00 00 05 01 87 61 24 19 44 00 06 2B" 我手动测试时，有空格和没空格，有区别吗
    直接 bytes.fromhex()：没有区别

    如果自己切字符串，就有区别
    hexstr = "7E0200" 
    hexstr[2:4]
    得到02

    hexstr = "7E 02 00" 
    hexstr[2:4]
    得到 " 0"
    因为空格占了一个字符

    JT808测试建议
    文件里可以写：7E 02 00 00 05 01 87 61 24 19 44 00 06 2B 7E
    方便人看。
    读取后：hexstr = hexstr.replace(" ", "")
    变成：7E0200000501876124194400062B7E
    再：data = bytes.fromhex(hexstr)
    或者更推荐：
    data = bytes.fromhex(hexstr)
    因为 bytes.fromhex() 本身支持忽略空格
    
"""
print(info)

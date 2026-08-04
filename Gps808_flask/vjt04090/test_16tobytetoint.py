# s = "0200" 
# print(f'两个十六进制字节: s={s}')

# b = bytes.fromhex(s)
# print(f'bytes.fromhex(s)  转成字节数据: b={b}') 

# n = int.from_bytes(b, "big")
# print(f'int.from_bytes(b, "big") 大端转整数: n={n}')

# xn = int.from_bytes(b, "little")
# print(f'int.from_bytes(b, "little") 小端转整数: xn={xn}')

# n2 = int.from_bytes(bytes.fromhex("0200"), "big")
# print(f'int.from_bytes直接转转整数: n={n}')

# two = bin(n)
# print(f'bin(n) 整数转二进制 0b表示这是二进制: two={two}')

# n = 126
# print(f"整数126：二进制 bin(126)={bin(n)}, 8位={n:08b}")
# print(f"整数126：十六进制{hex(n)}") 

# s = "7E"
# num = int(s, 16)
# print(f"7E十六进制：转整数{num}") 

# s = "01111110"
# num = int(s, 2)
# print(f"01111110二进制：转整数{num}") 


# data = b'\x7e'
# print(f"b\\x7e 字节转十六进制{data.hex()}") 

# data = b'\x7e'
# num = int.from_bytes(data, "big")
# print(f"b\\x7e 字节转整数{num}") 


# 126是字符串 转 二进制 和 十六进制 怎么写
# s = "126"
# n = int(s)
# print(f"字符串126 转整数 {n}") 
# print(f"字符串126 十六进制 {hex(n)}") 


b = bytes.fromhex("0180") #A064
b2 = int.from_bytes(b,"big")
print(f"0b{b2:016b}")
c=int.from_bytes(b,"big") & 0x8000
print(c)

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
    

    这三个表示的是同一个值：126 = 0b01111110 = 0x7E


    字节是数据存储单位规定：1 byte = 8 bit
    0111 1110 : 这 8 个二进制位，就是一个字节


    byte = 1字节
    2byte = 2字节
    Nbyte = N个字节
    bit = 位（1位，不是字节）
    WORD = 通常2字节
    DWORD = 通常4字节
"""
# print(info)

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

def format_and_print_hex(raw_hex_str):
    """
    将一连串紧凑的十六进制字符串，按照 ID、长度、数据的格式分行打印
    """
    # 1. 清理字符串：去掉可能存在的空格或换行符，全部转大写
    clean_hex = raw_hex_str.replace(" ", "").replace("\n", "").replace("\r", "").upper()
    
    i = 0
    total_len = len(clean_hex)
    
    print("=" * 25)
    print("ID   Len  Data")
    print("-" * 25)
    
    while i < total_len:
        # 安全防御：如果剩下的字符连 ID(4) 和 Len(2) 都凑不够，说明数据包不完整，直接退出
        if i + 6 > total_len:
            print(f"[剩余未解析的不完整数据: {clean_hex[i:]}]")
            break
            
        # 2. 提取 ID（2字节 = 4个字符）
        data_id = clean_hex[i:i+4]
        
        # 3. 提取 长度（1字节 = 2个字符），并转换成十进制整数
        len_hex = clean_hex[i+4:i+6]
        try:
            data_len = int(len_hex, 16)
        except ValueError:
            print(f"[错误] 长度字段 {len_hex} 无法解析为数字，解析中止。")
            break
            
        # 4. 根据提取出来的长度，计算出真实数据应该占用的字符数 (Len * 2)
        data_chars_count = data_len * 2
        
        # 安全防御：防止算出来的长度超出了字符串总长度
        if i + 6 + data_chars_count > total_len:
            print(f"[错误] ID {data_id} 声明数据长度为 {data_len} 字节，但后续数据不足。")
            print(f"当前剩余数据: {clean_hex[i:]}")
            break
            
        # 5. 提取真正的数据
        data_content = clean_hex[i+6 : i+6+data_chars_count]
        
        # 6. 漂亮地打印出来（:4 和 :2 用于控制格式对齐）
        print(f"{data_id} {len_hex} {data_content}")
        
        # 7. 指针向后移动，处理下一个数据块
        i += 6 + data_chars_count
        
    print("=" * 25)

# ----------------- 🧪 现场测试 -----------------

# 模拟你从串口拿到的一连串紧凑的、没排过版的十六进制长字符串
parse_ec_hexstr = (
    "60C002048560D0010C62F00201806050017660F001EE633001C86490011660A00251DE"
    "5005020069500A0202715112010051010192510201875103022C0A510402233E510501"
    "575107023D935108023ED65109020008510A0101510C014C52140206415224040000003352250400000033"
)

# 运行函数
format_and_print_hex(parse_ec_hexstr)

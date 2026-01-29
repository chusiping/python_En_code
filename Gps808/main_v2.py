import readdate_v2
import socket
import time
import temp
import testdate
import random
import argparse
import os
import re



# 仅此一行，全平台有效，0延迟
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 可选：Windows控制台优化（try保护，Linux自动跳过）
try:
    import ctypes
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
except:
    pass  # Linux上自动忽略，无需平台检查

def extract_number_from_brackets(text):
    """
    从字符串中提取括号内的数字
    例如："东(103)" -> 103
    """
    # 使用正则表达式提取
    match = re.search(r'\((\d+)\)', text)
    if match:
        return int(match.group(1))
    return None

def send_808_packet_tcp(packet_data, server_ip='14.23.86.188', server_port=6608):
    """
    使用TCP发送808协议数据包
    808协议通常使用TCP连接
    """
    sock = None
    try:
        # 创建TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)  # 设置超时时间
        
        print(f"    连接到 {server_ip}:{server_port}...")
        sock.connect((server_ip, server_port))
        print("     ✓ 连接成功!")
        
        print(f"    发送数据包 ({len(packet_data)} 字节)...")
        sock.sendall(packet_data)
        print("     ✓ 发送成功!")
        
        # 接收服务器响应
        print("  等待响应...")
        response = sock.recv(1024)
        
        if response:
            print(f"  ✓ 收到响应 ({len(response)} 字节):")
            print(f"    HEX: {response.hex().upper()}")
            # print(f"    明文: {zhuanhuan.parse_808_response(response)}")

        else:
            print("  ⓘ 收到空响应")
            
        return True, response
        
    except socket.timeout:
        print("  ✗ 连接或接收超时")
        return False, None
    except ConnectionRefusedError:
        print("  ✗ 连接被拒绝，服务器可能未启动")
        return False, None
    except Exception as e:
        print(f"  ✗ 错误: {type(e).__name__}: {e}")
        return False, None
    finally:
        if sock:
            try:
                sock.close()
            except:
                pass
def diff_seconds_safe(t1, t2):
    try:
        diff_sec = int(abs((t2 - t1).total_seconds()))
        return diff_sec
    except Exception:
        return 28


def main():
    #A方式测试： 服务器配置(独立测试使用)==============================================
    # _excleFile = "excle/轨迹列表.xlsx"    
    # _terminal_phone = "13301110130"         # 车牌号 "13305131386"  14926873647    
    # SERVER_IP = '14.23.86.188'              # 市平台 120.197.38.48  测试平台 14.23.86.188 
    # SERVER_PORT = 6608                      # 25209                          6608
    # SEND_TO_SERVER = False                   # 是否发送到服务器

    process_count = 0                       # 处理前2行数据
    _altitude_A = 10                        # 海拔
    _altitude_B = 15
    _satellite_count_A = 5                   #卫星数量
    _satellite_count_B = 10
    _miao = 2

    #B方式测试： 使用外部参数传入使用 ==================================================
    # 范例：python main_v2.py --excel "车充轨迹.xlsx" --phone 13301110130 --server-ip 14.23.86.188 --server-port 6608 --no-send
    parser = argparse.ArgumentParser(description='JT808数据发送')
    parser.add_argument('--excel', required=True, help='Excel文件路径')
    parser.add_argument('--phone', required=True, help='终端号码')
    parser.add_argument('--server-ip', required=True, help='服务器IP')
    parser.add_argument('--server-port', type=int, required=True, help='服务器端口')
    parser.add_argument('--send', dest='is_SEND', action='store_true',help='真实发送数据')
    parser.add_argument('--no-send', dest='is_SEND', action='store_false',help='测试模式不实际发送')
    parser.set_defaults(is_SEND=False)  # 默认值
    args = parser.parse_args()
    _excleFile = args.excel    
    _terminal_phone = args.phone           
    SERVER_IP = args.server_ip               
    SERVER_PORT = args.server_port   
    SEND_TO_SERVER =  args.is_SEND   

    # A和B只能选一种 ====================================================================
    miao,excel_data = readdate_v2.read_and_process_excel(_excleFile)
    # _miao = miao
    total_rows = len(excel_data)
    if process_count == 0:
        process_count = total_rows
    
    print(f"{'='*50}")
    if SEND_TO_SERVER:
        print(f"\n√[1] 正式发送: {SERVER_IP}:{SERVER_PORT} 间隔{_miao}秒")
    else:
        print(f"\n[1] 演示模式: 仅生成数据包，不真实发送。间隔{_miao}秒, 总{total_rows}行数据")
    print(f"    发送任务: {_excleFile} - 终端:{_terminal_phone} - 服务器:{SERVER_IP}:{SERVER_PORT}")
    print(f"")
    
    # 1. 读取Excel数据
    # print("\n[1] 读取Excel数据...")
    # miao,excel_data = readdate_v2.read_and_process_excel(_excleFile)
    # _miao = miao

    if not excel_data:
        print("读取数据失败，程序退出")
        return
    
    # total_rows = len(excel_data)
    # print(f"   ✓ 读取成功: {total_rows} 行数据")
    
    # if total_rows > 0:
    #     print(f"表头: {excel_data[0]}")
    
    # 统计数据
    success_count = 0
    fail_count = 0
    

    print(f"[2] 处理前{process_count}条记录:")

    GPS_lat = []
    GPS_long = []
    for i in range(0, min(process_count, total_rows)):  # 从第1行开始，跳过表头(改了)
        # print(f"\n{'='*50}")
        # print(f"\n  处理第 {i} 条记录:")
        
        try:
            # 提取数据
            terminal_phone = _terminal_phone  
            latitude = float(excel_data[i][6])       # 纬度
            longitude = float(excel_data[i][7])      # 经度
            _speed = int(excel_data[i][3])           # 速度 km/h
            speed = testdate.random_adjust(_speed,3)
            direction = extract_number_from_brackets(excel_data[i][4])       # 方向
            altitude = random.randint(_altitude_A, _altitude_B)                    # 随机取海拔
            mileage = 0
            msg_sn = 0
            alarm=0
            status=3             #0未开启未定位    1 ACC开启 + 未定位  acc开启是3
            brake_on=False       #刹车开启
            satellite_count=random.randint(_satellite_count_A, _satellite_count_B)    
            new_lat = 0
            new_lon = 0 
            # new_lat_t, new_lon_t = testdate.add_gps_noise(latitude, longitude, max_offset_meters=15)
            if i == 0 or excel_data[i][2] != excel_data[i-1][2]:
                new_lat, new_lon = testdate.add_gps_noise(latitude, longitude, max_offset_meters=15)
            else:
                new_lat = GPS_lat[i-1]
                new_lon = GPS_long[i-1]
            GPS_lat.append(new_lat)
            GPS_long.append(new_lon)

            if '里程：' in excel_data[i][5]:
                mileage_part = excel_data[i][5].split(';')[0].split('：')[1].split('km')[0]
                mileage = int(float(mileage_part)*10)
            if '制动信号' in excel_data[i][5]:
                brake_on = True
            if 'ACC关闭' in excel_data[i][5]:
                status = 2      #2 ACC 关闭 + 定位有效
            if 'ACC开启' in excel_data[i][5] and '未定位' in excel_data[i][5] :
                status = 1      #1 ACC开启 + 未定位
            
            # 增加判断两条数据之间的时间差秒，用来模仿真实数据的停顿
            if i + 1 < total_rows:
                _miao = diff_seconds_safe(excel_data[i][1], excel_data[i+1][1])

            # print(f"    平台: {SERVER_IP}:{SERVER_PORT}")
            # print(f"    手机: {terminal_phone}")
            # print(f"    纬度: {latitude} 偏移后{new_lat}")
            # print(f"    经度: {longitude} 偏移后{new_lon}")
            # print(f"    速度: {speed} km/h 偏移后{speed}"  )
            # print(f"    海拔: {altitude} 随机取")
            # print(f"    卫星: {satellite_count} ")
            # print(f"    方向: {direction}°")
            # print(f"    时间: {testdate.replace_date_to_today()}")
            # print(f"    制动: {brake_on}")

            print(f"    发送 {_terminal_phone} 第{i}/{total_rows}条记录 => 纬度: {latitude} 偏移后{new_lat} 经度: {longitude} 偏移后{new_lon} 速度: {speed} km/h 偏移后{speed} 海拔: {altitude} 随机取 卫星: {satellite_count} 方向: {direction} 制动: {brake_on} acc:{status}  等待{_miao}秒")
            # print(f"    纬度: {latitude} 偏移后{new_lat} 经度: {longitude} 偏移后{new_lon}")

            packet,raw = temp.build_0200(
                terminal_phone,
                new_lat,
                new_lon,
                altitude,
                speed,
                direction,
                testdate.replace_date_to_today(),
                mileage,
                msg_sn,
                alarm,
                status,
                brake_on,
                satellite_count
            )
            parsed = testdate.parse_gps_packet(packet.hex().upper())
            # testdate.pretty_print(parsed)

            
            if not packet:
                print("✗ 生成数据包失败")
                fail_count += 1
                continue
            
            # print(f"    ✓ 生成成功 ({len(packet)} 字节)")
            
            # 显示数据包信息
            # change808.print_packet_info(packet)
            
            # 发送数据包到服务器
            if SEND_TO_SERVER:
                print(f"\n[发送到服务器]")
                success, response = send_808_packet_tcp(packet, SERVER_IP, SERVER_PORT)
                
                if success:
                    success_count += 1
                    print(f"    ✓ 第{i}条记录处理完成")
                else:
                    fail_count += 1
                    print(f"    ✗ 第{i}条记录发送失败")
            else:
                success_count += 1
                # print(f"\nⓘ 演示模式: 跳过发送")
                # print(f"   数据包HEX: \n   {packet.hex().upper()}")
            
            # 添加延时，避免发送过快
            if i < min(process_count, total_rows) - 1:  # 不是最后一条
                # print(f"\n等待{_miao}秒...")
                time.sleep(_miao)
                
        except ValueError as e:
            print(f"✗ 数据转换错误: {e}")
            fail_count += 1
        except IndexError as e:
            print(f"✗ 数据索引错误: {e}")
            fail_count += 1
        except Exception as e:
            print(f"✗ 处理错误: {type(e).__name__}: {e}")
            fail_count += 1
    
    # 3. 询问是否处理剩余数据
    remaining = max(0, total_rows - process_count)
    # if remaining > 0:
        # print(f"\n{'='*60}")
        # print(f"\n[3]  还有 {remaining} 条记录未处理")
        
        # if SEND_TO_SERVER:
        #     choice = input(f"是否批量处理剩余数据？(y/n): ").lower()
        #     if choice == 'y':
        #         print(f"\n[3] 批量处理剩余数据...")
        #         print(f"将发送到: {SERVER_IP}:{SERVER_PORT}")
                
        #         batch_size = 10  # 每批处理数量
        #         total_batches = (remaining + batch_size - 1) // batch_size
                
        #         for batch in range(total_batches):
        #             start_idx = 4 + batch * batch_size
        #             end_idx = min(4 + (batch + 1) * batch_size, total_rows)
                    
        #             print(f"\n处理批次 {batch+1}/{total_batches} (记录 {start_idx} 到 {end_idx-1})")
                    
        #             for i in range(start_idx, end_idx):
        #                 try:
        #                     # 简化的数据提取
        #                     plate = str(excel_data[i][0])
        #                     lat = float(excel_data[i][5])
        #                     lon = float(excel_data[i][4])
        #                     spd = int(excel_data[i][3])
        #                     dir_val = int(excel_data[i][6])
                            
        #                     packet = change808.build_808_gps_message(plate, lat, lon, spd, dir_val, 0)
                            
        #                     if packet:
        #                         success, _ = send_808_packet_tcp(packet, SERVER_IP, SERVER_PORT)
        #                         if success:
        #                             success_count += 1
        #                             print(f"  ✓ 记录{i}发送成功")
        #                         else:
        #                             fail_count += 1
        #                             print(f"  ✗ 记录{i}发送失败")
        #                     else:
        #                         fail_count += 1
                                
        #                     # 每条记录间隔0.5秒
        #                     time.sleep(0.5)
                            
        #                 except Exception as e:
        #                     fail_count += 1
        #                     print(f"  ✗ 记录{i}处理失败: {e}")
                    
        #             # 每批之间间隔2秒
        #             if batch < total_batches - 1:
        #                 print(f"批次间隔2秒...")
        #                 time.sleep(2)
    

    print(f"\n[4] 统计结果 => 总记录数:{total_rows},还有{remaining}条记录未处理,成功处理: {success_count}  失败处理: {fail_count}")
    # 4. 显示统计结果
    # print(f"\n{'='*60}")
    # print("处理完成!")
    # print(f"{'='*60}")
    # print(f"统计结果:")
    # print(f"  总记录数: {total_rows - 1}")
    # print(f"  成功处理: {success_count}")
    # print(f"  失败处理: {fail_count}")
    
    # if total_rows - 1 > 0:
    #     success_rate = success_count / (total_rows - 1) * 100
    #     print(f"  成功率: {success_rate:.1f}%")
    
    if SEND_TO_SERVER:
        print(f"\n[4]  服务器: {SERVER_IP}:{SERVER_PORT} (TCP)  所有数据包已尝试发送")

if __name__ == "__main__":
    main()


# 2025-12-15 15:19 测试总结确认 (1)状态取值3 (2)经纬度方向上传正确    
# 2025-12-18 15:19 刹车状态在扩展字段，后续增加判断刹车，微调速度和经纬度
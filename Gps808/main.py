import readdate
import zhuanhuan
import socket
import time
import temp
import testdate
import random

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

def main():
    # 服务器配置
    SERVER_IP = '14.23.86.188'              # 市平台 120.197.38.48  测试平台 14.23.86.188 
    SERVER_PORT = 6608                      # 25209                          6608
    SEND_TO_SERVER = True                   # 是否发送到服务器
    _terminal_phone = "13301110130"         # 车牌号 "13305131386"  14926873647
    process_count = 200                       # 处理前2行数据
    _altitude_A = 10                        # 海拔
    _altitude_B = 15
    _satellite_count_A = 5                   #卫星数量
    _satellite_count_B = 10
    # print("=" * 60)
    # print("808协议数据包生成与TCP发送系统")

    
    if SEND_TO_SERVER:
        print(f"目标服务器: {SERVER_IP}:{SERVER_PORT}")
    else:
        print("演示模式: 仅生成数据包，不发送")

    
    # 1. 读取Excel数据
    print("\n[1] 读取Excel数据...")
    excel_data = readdate.read_excel_to_array("轨迹列表.xlsx")
    
    if not excel_data:
        print("读取数据失败，程序退出")
        return
    
    total_rows = len(excel_data)
    print(f"   ✓ 读取成功: {total_rows} 行数据")
    
    # if total_rows > 0:
    #     print(f"表头: {excel_data[0]}")
    
    # 统计数据
    success_count = 0
    fail_count = 0
    

    print(f"\n[2] 处理前{process_count}条记录:")
    
    for i in range(0, min(process_count, total_rows)):  # 从第1行开始，跳过表头(改了)
        print(f"\n{'='*50}")
        print(f"\n  处理第 {i} 条记录:")
        
        try:
            # 提取数据
            terminal_phone = _terminal_phone  
            latitude = float(excel_data[i][5])       # 纬度
            longitude = float(excel_data[i][4])      # 经度
            _speed = int(excel_data[i][3])           # 速度 km/h
            speed = testdate.random_adjust(_speed,3)
            direction = int(excel_data[i][6])       # 方向
            altitude = random.randint(_altitude_A, _altitude_B)                    # 随机取海拔
            timestr = excel_data[i][2]
            mileage = 0
            msg_sn = 0
            alarm=0
            status=3             #0未开启未定位    1 ACC开启 + 未定位  acc开启是3
            brake_on=False       #刹车开启
            satellite_count=random.randint(_satellite_count_A, _satellite_count_B)    
            new_lat, new_lon = testdate.add_gps_noise(latitude, longitude, max_offset_meters=15)

            if '里程：' in excel_data[i][8]:
                mileage_part = excel_data[i][8].split(';')[0].split('：')[1].split('km')[0]
                mileage = int(float(mileage_part)*10)
            if '刹车' in excel_data[i][8]:
                brake_on = True

            print(f"    平台: {SERVER_IP}:{SERVER_PORT}")
            print(f"    手机: {terminal_phone}")
            print(f"    车牌: {terminal_phone}")
            print(f"    纬度: {latitude} 偏移后{new_lat}")
            print(f"    经度: {longitude} 偏移后{new_lon}")
            print(f"    速度: {speed} km/h 偏移后{speed}"  )
            print(f"    海拔: {altitude} 随机取")
            print(f"    卫星: {satellite_count} ")
            print(f"    方向: {direction}°")
            print(f"    时间: {testdate.replace_date_to_today()}")
            print(f"    刹车: {brake_on}")



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
            testdate.pretty_print(parsed)

            
            if not packet:
                print("✗ 生成数据包失败")
                fail_count += 1
                continue
            
            print(f"    ✓ 生成成功 ({len(packet)} 字节)")
            
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
                print(f"\nⓘ 演示模式: 跳过发送")
                print(f"   数据包HEX: \n   {packet.hex().upper()}")
            
            # 添加延时，避免发送过快
            if i < min(process_count, total_rows) - 1:  # 不是最后一条
                print(f"\n等待2秒...")
                time.sleep(3)
                
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
    remaining = max(0, total_rows - 4)
    if remaining > 0:
        print(f"\n{'='*60}")
        print(f"还有 {remaining} 条记录未处理")
        
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
    
    # 4. 显示统计结果
    print(f"\n{'='*60}")
    print("处理完成!")
    print(f"{'='*60}")
    print(f"统计结果:")
    print(f"  总记录数: {total_rows - 1}")
    print(f"  成功处理: {success_count}")
    print(f"  失败处理: {fail_count}")
    
    if total_rows - 1 > 0:
        success_rate = success_count / (total_rows - 1) * 100
        print(f"  成功率: {success_rate:.1f}%")
    
    if SEND_TO_SERVER:
        print(f"\n服务器: {SERVER_IP}:{SERVER_PORT} (TCP)")
        print("所有数据包已尝试发送")

if __name__ == "__main__":
    main()


# 2025-12-15 15:19 测试总结确认 (1)状态取值3 (2)经纬度方向上传正确    
# 2025-12-18 15:19 刹车状态在扩展字段，后续增加判断刹车，微调速度和经纬度
import readdate
import change808
import change808_b
import zhuanhuan
import socket
import time

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
        
        print(f"  连接到 {server_ip}:{server_port}...")
        sock.connect((server_ip, server_port))
        print("  ✓ 连接成功!")
        
        print(f"  发送数据包 ({len(packet_data)} 字节)...")
        sock.sendall(packet_data)
        print("  ✓ 发送成功!")
        
        # 接收服务器响应
        print("  等待响应...")
        response = sock.recv(1024)
        
        if response:
            print(f"  ✓ 收到响应 ({len(response)} 字节):")
            print(f"    HEX: {response.hex().upper()[:80]}...")
            print(f"    明文: {zhuanhuan.parse_808_response(response)}")

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
    SERVER_IP = '14.23.86.188'
    SERVER_PORT = 6608
    SEND_TO_SERVER = True  # 是否发送到服务器
    phone_number="13305131386"
    
    print("=" * 60)
    print("808协议数据包生成与TCP发送系统")

    
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
    print(f"✓ 读取成功: {total_rows} 行数据")
    
    if total_rows > 0:
        print(f"表头: {excel_data[0]}")
    
    # 统计数据
    success_count = 0
    fail_count = 0
    
    # 2. 处理前3行数据
    print(f"\n[2] 处理前3条记录:")
    
    for i in range(1, min(4, total_rows)):  # 从第1行开始，跳过表头
        print(f"\n{'='*50}")
        print(f"处理第 {i} 条记录:")
        
        try:
            converter = change808_b.JTT808Converter(phone_number)
            vehicle_data = converter.parse_position_data(excel_data[i])
            packet = converter.create_position_message(vehicle_data)

            print(f"\n生成的JTT808数据包 ({len(packet)} 字节):")
            print(f"HEX: {packet.hex().upper()}")

            if not packet:
                print("✗ 生成数据包失败")
                fail_count += 1
                continue
            
            print(f"✓ 生成成功 ({len(packet)} 字节)")
            
            # 显示数据包信息
            # change808.print_packet_info(packet)
            
            # 发送数据包到服务器
            if SEND_TO_SERVER:
                print(f"\n[发送到服务器]")
                success, response = send_808_packet_tcp(packet, SERVER_IP, SERVER_PORT)
                
                if success:
                    success_count += 1
                    print(f"✓ 第{i}条记录处理完成")
                else:
                    fail_count += 1
                    print(f"✗ 第{i}条记录发送失败")
            else:
                success_count += 1
                print(f"\nⓘ 演示模式: 跳过发送")
                print(f"  数据包HEX: {packet.hex().upper()[:60]}...")
            
            # 添加延时，避免发送过快
            if i < min(4, total_rows) - 1:  # 不是最后一条
                print(f"\n等待2秒...")
                time.sleep(2)
                
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
        
        if SEND_TO_SERVER:
            choice = input(f"是否批量处理剩余数据？(y/n): ").lower()
            if choice == 'y':
                print(f"\n[3] 批量处理剩余数据...")
                print(f"将发送到: {SERVER_IP}:{SERVER_PORT}")
                
                batch_size = 10  # 每批处理数量
                total_batches = (remaining + batch_size - 1) // batch_size
                
                for batch in range(total_batches):
                    start_idx = 4 + batch * batch_size
                    end_idx = min(4 + (batch + 1) * batch_size, total_rows)
                    
                    print(f"\n处理批次 {batch+1}/{total_batches} (记录 {start_idx} 到 {end_idx-1})")
                    
                    for i in range(start_idx, end_idx):
                        try:
                            converter = change808_b.JTT808Converter(phone_number)
                            vehicle_data = converter.parse_position_data(excel_data[i])
                            packet = converter.create_position_message(vehicle_data)
                            
                            if packet:
                                success, _ = send_808_packet_tcp(packet, SERVER_IP, SERVER_PORT)
                                if success:
                                    success_count += 1
                                    print(f"  ✓ 记录{i}发送成功")
                                else:
                                    fail_count += 1
                                    print(f"  ✗ 记录{i}发送失败")
                            else:
                                fail_count += 1
                                
                            # 每条记录间隔0.5秒
                            time.sleep(0.5)
                            
                        except Exception as e:
                            fail_count += 1
                            print(f"  ✗ 记录{i}处理失败: {e}")
                    
                    # 每批之间间隔2秒
                    if batch < total_batches - 1:
                        print(f"批次间隔2秒...")
                        time.sleep(2)
    
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
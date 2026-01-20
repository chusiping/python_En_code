import pandas as pd

def read_and_process_excel(file_path):
    """读取并处理Excel文件"""
    # 读取数据
    try:
        df = pd.read_excel(file_path, header=3)
        
        # 重命名列
        df.columns = ['序号', '时间', '经纬度', '速度', '行驶方向', '状态']
        
        # 转换时间列
        df['时间'] = pd.to_datetime(df['时间'])
        
        # 拆分经纬度
        df[['纬度', '经度']] = df['经纬度'].str.split(',', expand=True)
        df['纬度'] = df['纬度'].astype(float)
        df['经度'] = df['经度'].astype(float)
        
        headers = df.columns.tolist()  # 表头
        rows = df.values.tolist()      # 数据行
        result = rows

        return df,result

    except Exception as e:
        print(f"读取文件失败: {e}")
        return None


# 主程序
if __name__ == "__main__":
    # 读取数据
    file_path = '车充轨迹.xlsx'
    df,data = read_and_process_excel(file_path)

    if data:
        # print(f"\n前3行数据:")
        for i in range(min(14, len(data))):
            print(f"行{i}: {data[i]}")

    # # 设置显示选项
    # pd.set_option('display.max_rows', None)  # 显示所有行
    # pd.set_option('display.max_columns', None)  # 显示所有列
    # pd.set_option('display.width', 150)  # 显示宽度
    
    # # 打印完整数据
    # print("=" * 120)
    # print("完整数据内容:")
    # print("=" * 120)
    # print(df)
    # print("=" * 120)
    
    # # 打印基本信息
    # print(f"\n数据基本信息:")
    # print(f"总行数: {len(df)}")
    # print(f"时间范围: {df['时间'].min()} 到 {df['时间'].max()}")
    # print(f"列名: {list(df.columns)}")
    
    # # 保存数据
    # df.to_excel('处理后的车充轨迹.xlsx', index=False)
    # print("\n数据已保存到 '处理后的车充轨迹.xlsx'")
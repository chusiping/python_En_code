import pandas as pd

def read_excel_to_array(file_path, selected_columns=None):
    """
    读取Excel文件并返回二维数组
    参数: 
        file_path - Excel文件路径
        selected_columns - 要读取的列头名称列表，如 ["车牌号码", "定位时间", "经度", "维度", "方向", "速度(km/h)"]
    返回: 二维数组 [表头, 数据行1, 数据行2, ...]
    """
    try:
        # 读取整个Excel文件
        df = pd.read_excel(file_path, dtype=str)
        
        if selected_columns:
            # 检查哪些列名存在
            existing_columns = []
            for col in selected_columns:
                if col in df.columns:
                    existing_columns.append(col)
                else:
                    print(f"警告: 列 '{col}' 不存在于文件中")
            
            if existing_columns:
                # 只选择存在的列
                df = df[existing_columns]
                # print(f"读取指定列: {existing_columns}")
            else:
                print("错误: 指定的列都不存在，读取所有列")
        
        # 转换为二维数组
        headers = df.columns.tolist()  # 表头
        rows = df.values.tolist()      # 数据行
        
        # 合并为完整数组
        # result = [headers] + rows  带列头 
        result = rows
        
        # print(f"读取成功: {len(result)} 行数据，{len(headers)} 列")
        return result
        
    except Exception as e:
        print(f"读取文件失败: {e}")
        return None

# 可以单独测试
if __name__ == "__main__":

    columns_to_read = ["车牌号码","是否定位", "定位时间", "速度(km/h)", "经度", "维度", "方向","详细地址","状态"]
    
    # 调用函数
    data = read_excel_to_array("轨迹列表.xlsx", selected_columns=columns_to_read)
    
    if data:
        # print(f"\n前3行数据:")
        for i in range(min(4, len(data))):
            print(f"行{i}: {data[i]}")
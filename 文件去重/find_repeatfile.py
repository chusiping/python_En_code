import os
import hashlib
import argparse

parser = argparse.ArgumentParser(description='查找并删除重复文件')
parser.add_argument('root_dir', help='要扫描的目录路径')
args = parser.parse_args()

root_dir = args.root_dir

hash_dict = {}

def get_md5(file_path):
    md5 = hashlib.md5()

    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            md5.update(chunk)

    return md5.hexdigest()

# 遍历所有文件
for root, dirs, files in os.walk(root_dir):
    for file in files:

        full_path = os.path.join(root, file)

        try:
            file_size = os.path.getsize(full_path)

            # 先用大小
            key = (file_size, get_md5(full_path))

            if key not in hash_dict:
                hash_dict[key] = [full_path]
            else:
                hash_dict[key].append(full_path)

        except Exception as e:
            print("错误:", full_path, e)

# 输出重复文件
for key, file_list in hash_dict.items():

    if len(file_list) > 1:

        print("\n发现重复文件：")

        for f in file_list:
            print(f)

        # 保留第一个
        for duplicate in file_list[1:]:

            try:
                os.remove(duplicate)
                print("已删除:", duplicate)

            except Exception as e:
                print("删除失败:", duplicate, e)
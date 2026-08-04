import os
import json
import argparse
from parser import parse_jt808_packet
from save_result import * 
import sys

import re

def find_unparsed_data(text):
    """
    查找字符串中疑似未解析的数据片段
    特征：
    - 英文字母 + 数字混合
    - 连续长度 >= 4
    """

    pattern = r'\b(?=[A-Za-z0-9]*[A-Za-z])(?=[A-Za-z0-9]*\d)[A-Za-z0-9]+\b'

    return re.findall(pattern, text)

def find_unparsed_in_json(data):
    result = []

    if isinstance(data, dict):
        for k, v in data.items():
            result.extend(find_unparsed_in_json(v))
    elif isinstance(data, list):
        for v in data:
            result.extend(find_unparsed_in_json(v))
    elif isinstance(data, str):
        # 英文数字混合
        result.extend(find_unparsed_data(data))
    return result



def main():
    parser = argparse.ArgumentParser(
        description="JT808协议测试工具"
    )
    parser.add_argument(
        "--file",
        "-f",
        required=True,
        help="测试txt文件"
    )
    args = parser.parse_args()
    txt_file=args.file
    if not os.path.exists(txt_file):
        print(
            f"文件不存在:{txt_file}"
        )
        return
    # ==========================
    # 输出目录
    # ==========================
    result_dir="result"
    os.makedirs(
        result_dir,
        exist_ok=True
    )
    # 文件名
    base_name=os.path.splitext(
        os.path.basename(txt_file)
    )[0]
    # ==========================
    # 逐行读取
    # ==========================
    with open(
        txt_file,
        "r",
        encoding="utf-8"
    ) as f:
        for line_no,line in enumerate(
            f,
            start=1
        ):
            hexstr=line.strip()
            # 跳过空行
            if not hexstr:
                continue
            print("\n" + "="*60)
            print(
                f"正在解析 {base_name} 第 {line_no} 行"
            )
            print(hexstr)

            bad = find_unparsed_in_json(hexstr)
            for x in bad:
                print("发现未解析:", x)
                hexstr

            try:
                result=parse_jt808_packet(
                    hexstr
                )
                print("\n解析结果:")
                print(
                    json.dumps(
                        result,
                        ensure_ascii=False,
                        indent=4
                    )
                )
                # ==========================
                # 保存结果
                # ==========================
                filename = save_result(result)
            except Exception as e:
                print(
                    "解析失败:",
                    e
                )
            # ==========================
            # 等待确认
            # ==========================
            cmd=input(
                "\n输入回车继续，输入 q 退出:"
            )
            if cmd.lower()=="q":
                print(
                    "退出测试"
                )
                break
if __name__=="__main__":
    sys.argv = [
        "test_for.py",
        "-f",
        "测试包/0200_0803.txt"
    ]
    main()
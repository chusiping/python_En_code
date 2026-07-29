import os
import json
import argparse
from parser import parse_jt808_packet

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
                out_file=os.path.join(
                    result_dir,
                    f"{base_name}_{line_no}.json"
                )
                with open(
                    out_file,
                    "w",
                    encoding="utf-8"
                ) as out:
                    json.dump(
                        result,
                        out,
                        ensure_ascii=False,
                        indent=4
                    )
                print(
                    f"\n保存:{out_file}"
                )
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
    main()
import os
from datetime import datetime
def save_log(data, addr=None):
    # 日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # 按日期生成文件
    filename = datetime.now().strftime(
        "%Y-%m-%d"
    ) + ".log"
    filepath = os.path.join(
        log_dir,
        filename
    )
    # hex字符串
    hexstr = data.hex().upper()
    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    with open(
        filepath,
        "a",
        encoding="utf-8"
    ) as f:
        f.write(
            f"{now} "
        )
        if addr:
            f.write(
                f"{addr} "
            )
        f.write(
            hexstr
        )
        f.write(
            "\n"
        )
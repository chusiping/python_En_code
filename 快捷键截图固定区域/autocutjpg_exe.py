import argparse
import keyboard
import mss
import mss.tools
import os
import sys
import tkinter as tk
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--directory', default='output')
args = parser.parse_args()

output_dir = args.directory

screenshot_count = 0


def shot():
    """执行截图: 屏幕区域 (1,80) 起始的 1910x910"""
    global screenshot_count
    try:
        os.makedirs(output_dir, exist_ok=True)
        with mss.mss() as sct:
            filename = os.path.join(
                output_dir,
                datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
            )
            region = {"left": 1, "top": 80, "width": 1910, "height": 910}
            img = sct.grab(region)
            mss.tools.to_png(img.rgb, img.size, output=filename)
        screenshot_count += 1
        if root.winfo_exists():
            root.after(0, update_label)
    except Exception as e:
        if root.winfo_exists():
            root.after(0, lambda: status_label.config(
                text=f"错误: {e}", fg="red"))


def update_label():
    count_label.config(text=f"已截图: {screenshot_count}")
    path_label.config(text=f"保存到: {os.path.abspath(output_dir)}")
    status_label.config(text="")  # 清空错误提示


def on_close():
    """退出: 注销热键, 销毁窗口, 终止进程"""
    try:
        keyboard.unhook_all_hotkeys()
    except Exception:
        pass
    try:
        root.destroy()
    except Exception:
        pass
    sys.exit(0)


# ---- 主窗口 ----
root = tk.Tk()
root.title("区域截图工具")
root.attributes('-topmost', True)        # 窗口置顶
root.resizable(False, False)

# 定位到桌面右下角 (留出任务栏空间)
window_width = 300
window_height = 150
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
x = screen_w - window_width - 10
y = screen_h - window_height - 60
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# 界面元素
info_label = tk.Label(
    root, text="快捷键 F4  |  区域: (1,80) 1910x910",
    font=("Microsoft YaHei", 9))
info_label.pack(pady=(8, 4))

count_label = tk.Label(root, text="已截图: 0", font=("Microsoft YaHei", 9))
count_label.pack()

path_label = tk.Label(
    root, text="", font=("Microsoft YaHei", 8), fg="gray", wraplength=280)
path_label.pack(pady=2)

status_label = tk.Label(root, text="", font=("Microsoft YaHei", 8), fg="red")
status_label.pack()

btn_frame = tk.Frame(root)
btn_frame.pack(pady=6)

shot_btn = tk.Button(btn_frame, text="📷 截图", command=shot, width=8)
shot_btn.pack(side=tk.LEFT, padx=6)

exit_btn = tk.Button(btn_frame, text="退出", command=on_close, width=8)
exit_btn.pack(side=tk.LEFT, padx=6)

update_label()

# 注册全局热键 (keyboard 库自带后台监听线程, 不阻塞 tkinter)
keyboard.add_hotkey('F4', shot)

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

import io
import json
import os
import sys
import tkinter as tk

import keyboard
import mss
import win32clipboard
from PIL import Image
import winsound

screenshot_count = 0

DEFAULT_REGION = {"left": 38, "top": 113, "width": 1230, "height": 560}


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


CONFIG_PATH = os.path.join(app_dir(), "config.json")


def load_region():
    """从 config.json 读取截图区域，文件缺失或字段不全时返回默认值"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        region = {**DEFAULT_REGION, **cfg.get("region", {})}
        return region
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULT_REGION)


def shot():
    """截取屏幕区域 (从 config.json 读取), 复制到剪贴板"""
    global screenshot_count
    try:
        region = load_region()
        with mss.mss() as sct:
            img = sct.grab(region)
            pil_img = Image.frombytes("RGB", img.size, img.rgb)

        # PIL 保存的 BMP 头部带 14 字节 BITMAPFILEHEADER, CF_DIB 只需要 BITMAPINFOHEADER 起的内容
        output = io.BytesIO()
        pil_img.save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        winsound.MessageBeep() 

        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        finally:
            win32clipboard.CloseClipboard()

        screenshot_count += 1
        if root.winfo_exists():
            root.after(0, update_label)
    except Exception as e:
        if root.winfo_exists():
            root.after(0, lambda: status_label.config(
                text=f"错误: {e}", fg="red"))


def update_label():
    count_label.config(text=f"已复制: {screenshot_count}")
    status_label.config(text="")


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
root.attributes('-topmost', True)
root.resizable(False, False)

window_width = 300
window_height = 120
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
x = screen_w - window_width - 10
y = screen_h - window_height - 60
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

region = load_region()
info_text = (
    f"快捷键 F4  |  区域: ({region['left']},{region['top']}) "
    f"{region['width']}x{region['height']}\n截图复制到剪贴板"
)
info_label = tk.Label(root, text=info_text, font=("Microsoft YaHei", 9))
info_label.pack(pady=(8, 4))

count_label = tk.Label(root, text="已复制: 0", font=("Microsoft YaHei", 9))
count_label.pack()

status_label = tk.Label(root, text="", font=("Microsoft YaHei", 8), fg="red")
status_label.pack()

btn_frame = tk.Frame(root)
btn_frame.pack(pady=6)

shot_btn = tk.Button(btn_frame, text="📋 复制", command=shot, width=8)
shot_btn.pack(side=tk.LEFT, padx=6)

exit_btn = tk.Button(btn_frame, text="退出", command=on_close, width=8)
exit_btn.pack(side=tk.LEFT, padx=6)

update_label()

keyboard.add_hotkey('F4', shot)

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()

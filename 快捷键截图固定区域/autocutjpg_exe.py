import io
import sys
import tkinter as tk

import keyboard
import mss
import win32clipboard
from PIL import Image
import winsound

screenshot_count = 0


def shot():
    """截取屏幕区域 (1,80) 1910x910, 复制到剪贴板"""
    global screenshot_count
    try:
        with mss.mss() as sct:
            region = {"left": 38, "top": 113, "width": 1230, "height": 560}
            img = sct.grab(region)
            pil_img = Image.frombytes("RGB", img.size, img.rgb)

        # PIL 保存的 BMP 头部带 14 字节 BITMAPFILEHEADER, CF_DIB 只需要 BITMAPINFOHEADER 起的内容
        output = io.BytesIO()
        pil_img.save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()
        winsound.MessageBeep() 

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
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

info_label = tk.Label(
    root, text="快捷键 F4  |  区域: (1,80) 1910x910\n截图复制到剪贴板",
    font=("Microsoft YaHei", 9))
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

import argparse
import keyboard
import mss
from PIL import Image
from io import BytesIO
import win32clipboard

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--directory', default='output')
args = parser.parse_args()


def copy_image_to_clipboard(img):
    # MSS截图转PIL图片
    image = Image.frombytes(
        "RGB",
        img.size,
        img.rgb
    )

    output = BytesIO()

    # 剪贴板需要BMP格式，且去掉14字节文件头
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]

    output.close()

    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(
            win32clipboard.CF_DIB,
            data
        )
    finally:
        win32clipboard.CloseClipboard()


def shot():
    with mss.mss() as sct:
        region = {
            "left": 38,
            "top": 113,
            "width": 1230,
            "height": 560
        }

        img = sct.grab(region)
        copy_image_to_clipboard(img)

        print("截图已复制到剪贴板")


keyboard.add_hotkey('F4', shot)

print("按 F4 截图并复制到剪贴板")
keyboard.wait()
import argparse
import keyboard
import mss
import mss.tools
import time
import os
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--directory', default='output')
args = parser.parse_args()

output_dir = args.directory

def shot():
    os.makedirs(output_dir, exist_ok=True)

    with mss.mss() as sct:
        filename = os.path.join(
            output_dir,
            datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
        )

        img = sct.grab(sct.monitors[1])
        mss.tools.to_png(img.rgb, img.size, output=filename)

keyboard.add_hotkey('F4', shot)

keyboard.wait()
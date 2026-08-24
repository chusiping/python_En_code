1 配置
开启 Windows 隐藏的“立体声混音”这是最传统、最稳定的 Windows 内录通道，
开启后 Python 就能像识别麦克风一样识别它：按键盘上的 Win + R 键打开运行窗口，
输入 mmsys.cpl 并敲回车（这会直接打开经典的“声音”控制面板）。
在弹出的窗口顶部，点击 “录制” (Recording) 选项卡。在空白的地方右键点击，
勾选 “显示禁用的设备” (Show Disabled Devices)。
这时列表里应该会出现一个带有灰色喇叭图标的 “立体声混音” (Stereo Mix) 或 “Wave Out Mix”。
右键点击它，选择 “启用” (Enable

2 打包
pyinstaller --onefile --console --add-binary "ffmpeg.exe;." --add-binary "ffprobe.exe;." start.py

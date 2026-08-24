import sounddevice as sd
import soundfile as sf
import queue
import sys
import time
import os
from pydub import AudioSegment  # 引入音频转换库

# ================= 1. 环境路径兼容与 FFmpeg 配置 =================
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

AudioSegment.converter = os.path.join(base_path, "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(base_path, "ffprobe.exe")

# ================= 2. 自动寻找立体声混音设备 =================
def find_stereo_mix_id():
    devices = sd.query_devices()
    for idx, d in enumerate(devices):
        if ('混音' in d['name'] or 'Stereo Mix' in d['name'] or 'Wave Out' in d['name']) and d['max_input_channels'] > 0:
            return idx
    return None

target_device_id = find_stereo_mix_id()

if target_device_id is None:
    print("❌ 找不到“立体声混音”设备！")
    sys.exit()

device_info = sd.query_devices(target_device_id)
sample_rate = int(device_info['default_samplerate'])
channels = 2

# ================= 3. 🛠️ 新增：用户输入定时逻辑 =================
print("=" * 50)

user_input = input("1. 请输入录制时长（单位：分钟，直接回车默认为 1 分钟）: ").strip()

# 如果用户直接回车，或者输入的不是纯数字，则默认设为 1 分钟
if not user_input or not user_input.isdigit():
    target_minutes = 1.0
else:
    target_minutes = float(user_input)

# 将分钟转换为秒数，方便后续判断
target_seconds = int(target_minutes * 60)

print(f"2. 录制计划已设定：将在录满 {target_minutes} 分钟 ({target_seconds} 秒) 后自动停止并转换。")

# ================= 4. 配置文件名与队列 =================
timestamp = int(time.time())
temp_wav = f"temp_{timestamp}.wav"
final_mp3 = f"record_{timestamp}.mp3"

audio_queue = queue.Queue()

def callback(indata, frames, time_info, status):
    if status:
        print(f"⚠️ 状态警告: {status}", file=sys.stderr)
    audio_queue.put(indata.copy())

print(f"3. 成功对接 Windows 系统混音通道！")
print(f"4. 录制目标设备: [{target_device_id}] - {device_info['name']}")
print(f"5. 采样率: {sample_rate}Hz | 声道: {channels}")

# ================= 5. 核心录音与定时判断逻辑 =================
try:
    with sd.InputStream(samplerate=sample_rate, 
                         device=target_device_id, 
                         channels=channels, 
                         blocksize=4096, 
                         callback=callback):
        
        with sf.SoundFile(temp_wav, mode='x', samplerate=sample_rate, channels=channels) as file:
            print("6. 开始持续内录！请播放电脑里的声音...")
            print("   提示：达到设定时间会自动结束。期间你也可以随时按 Ctrl + C 提前结束并保存。")
            print("-" * 50)
            
            start_time = time.time()
            last_hint_time = 0

            while True:
                # 写入音频数据
                file.write(audio_queue.get())
                
                # 计算已经录制了多少秒
                elapsed_seconds = int(time.time() - start_time)
                
                # 🛠️ 核心优化 1：达到预设的定时秒数，自动 break 退出循环
                if elapsed_seconds >= target_seconds:
                    print(f"⏰ 预定时间已到 ({target_minutes} 分钟)，正在自动结束录音...")
                    break
                
                # 每过 10 秒提示一次
                if elapsed_seconds > 0 and elapsed_seconds % 10 == 0 and elapsed_seconds != last_hint_time:
                    last_hint_time = elapsed_seconds
                    
                    if elapsed_seconds < 60:
                        print(f"⏰ 已经录制了 {elapsed_seconds} 秒了... (目标: {target_seconds} 秒)")
                    else:
                        minutes = elapsed_seconds // 60
                        seconds = elapsed_seconds % 60
                        if seconds == 0:
                            print(f"⏰ 已经录制了 {minutes} 分钟了... (目标: {target_minutes} 分钟)")
                        else:
                            print(f"⏰ 已经录制了 {minutes} 分 {seconds} 秒了... (目标: {target_minutes} 分钟)")

except KeyboardInterrupt:
    print("\n" + "-" * 50)
    print("🛑 收到手动停止指令！正在提前结束...")

# ================= 6. 自动执行 MP3 转换 =================
print("7. 正在全力转换为 MP3 格式，请稍候...")
try:
    sound = AudioSegment.from_wav(temp_wav)
    sound.export(final_mp3, format="mp3", bitrate="192k")
    
    if os.path.exists(temp_wav):
        os.remove(temp_wav)
        
    print(f"6. 精彩！音频已成功转换为压缩格式，保存至: {final_mp3}")
    
except Exception as conv_err:
    print(f"❌ WAV 转 MP3 失败。请检查是否安装了 FFmpeg。错误信息: {conv_err}")
    print(f"💡 临时的无损录音文件仍保留在: {temp_wav}")
except Exception as e:
    print(f"\n❌ 录音中途意外中断。错误信息: {e}")

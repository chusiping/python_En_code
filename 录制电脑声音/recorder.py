import sounddevice as sd
import soundfile as sf
import queue
import sys
import time
import os
from pydub import AudioSegment  # 引入音频转换库

if getattr(sys, 'frozen', False):
    # 如果是运行打包后的 exe
    base_path = sys._MEIPASS
else:
    # 如果是直接运行 .py 脚本
    base_path = os.path.dirname(os.path.abspath(__file__))

# 强行指定 pydub 的 ffmpeg 寻找路径为当前释放的目录
AudioSegment.converter = os.path.join(base_path, "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(base_path, "ffprobe.exe")


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

# 🛠️ 配置文件名
timestamp = int(time.time())
temp_wav = f"temp_{timestamp}.wav"   # 录音时的临时无损文件
final_mp3 = f"record_{timestamp}.mp3" # 最终想要生成的 MP3 文件

audio_queue = queue.Queue()

def callback(indata, frames, time_info, status):
    if status:
        print(f"⚠️ 状态警告: {status}", file=sys.stderr)
    audio_queue.put(indata.copy())

print(f"1. 成功对接 Windows 系统混音通道！")
print(f"2. 录制目标设备: [{target_device_id}] - {device_info['name']}")
print(f"3. 采样率: {sample_rate}Hz | 声道: {channels}")

try:
    with sd.InputStream(samplerate=sample_rate, 
                         device=target_device_id, 
                         channels=channels, 
                         blocksize=4096, 
                         callback=callback):
        
        # 先录制到临时 WAV 文件中
        with sf.SoundFile(temp_wav, mode='x', samplerate=sample_rate, channels=channels) as file:
            print("4. 开始持续内录！请播放电脑里的声音...")
            print("按 Ctrl + C 可以随时停止录音并保存为 MP3。")
            
            while True:
                file.write(audio_queue.get())

except KeyboardInterrupt:
    print("5. 录音捕获结束！正在全力转换为 MP3 格式，请稍候...")
    
    try:
        # 🛠️ 核心逻辑：读取临时 WAV，压缩并导出为标准 MP3
        sound = AudioSegment.from_wav(temp_wav)
        # bitrate="192k" 是高音质 MP3 的标准（如果想要更高，可以改为 320k）
        sound.export(final_mp3, format="mp3", bitrate="192k")
        
        # 转换成功后，删除无用的临时 WAV 文件
        if os.path.exists(temp_wav):
            os.remove(temp_wav)
            
        print(f"6. 精彩！音频已成功转换为压缩格式，保存至: {final_mp3}")
        
    except Exception as conv_err:
        print(f"❌ WAV 转 MP3 失败。请检查是否安装了 FFmpeg。错误信息: {conv_err}")
        print(f"💡 临时的无损录音文件仍保留在: {temp_wav}")

except Exception as e:
    print(f"\n❌ 录音中途意外中断。错误信息: {e}")

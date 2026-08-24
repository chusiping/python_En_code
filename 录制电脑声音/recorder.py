import sounddevice as sd
import soundfile as sf
import queue
import sys
import time

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

filename = f"record_{int(time.time())}.wav" # 使用时间戳，防止文件冲突报错
audio_queue = queue.Queue()

def callback(indata, frames, time_info, status):
    if status:
        # 如果系统有任何卡顿或警告，实时打印出来，不憋着报错
        print(f"⚠️ 状态警告: {status}", file=sys.stderr)
    audio_queue.put(indata.copy())

print(f"✅ 成功对接 Windows 系统混音通道！")
print(f"🎛️ 录制目标设备: [{target_device_id}] - {device_info['name']}")
print(f"🎵 采样率: {sample_rate}Hz | 声道: {channels}")

try:
    # 🛠️ 核心修正：显式指定 blocksize（缓冲区大小），防止一秒断开
    with sd.InputStream(samplerate=sample_rate, 
                         device=target_device_id, 
                         channels=channels, 
                         blocksize=4096,  # 增大缓冲区，稳定音频流
                         callback=callback):
        
        with sf.SoundFile(filename, mode='x', samplerate=sample_rate, channels=channels) as file:
            print("\n▶️ 开始持续内录！请播放电脑里的声音...")
            print("按 Ctrl + C 可以随时停止录音并保存。")
            
            while True:
                # 阻塞式获取数据并写入，确保主线程不退出
                data = audio_queue.get()
                file.write(data)

except KeyboardInterrupt:
    print(f"\n🛑 录音捕获结束！文件已成功保存至: {filename}")
except Exception as e:
    print(f"\n❌ 录音中途意外中断。错误信息: {e}")

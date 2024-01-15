import ffmpy
import os
import subprocess
import sys

ffmpeg_path = r'D:\lvse\ffmpeg\bin\ffmpeg.exe'

def convert_to_seconds(time_str):
    hours, minutes, seconds = map(int, time_str.split(':'))
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds

def convert_to_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return time_str

def get_video_duration(video_path):
    # 调用FFmpeg命令获取视频信息
    command = [ffmpeg_path, '-i', video_path]
    result = subprocess.run(command, capture_output=True, text=True)

    # 从输出中提取视频时长信息
    output = result.stderr
    duration_line = [line for line in output.split('\n') if 'Duration' in line][0]
    duration = duration_line.split('Duration: ')[1].split(',')[0]
    duration = duration.split('.')[0]

    return duration

sourceFile = input("请输入视频文件：").replace('"', '')
time_str1 = get_video_duration(sourceFile)   
time_str2 = input("请输入第二个时间值（格式为 HH:MM:SS）：")
     

# sourceFile = r'C:\Users\Administrator\Desktop\新建文件夹\a.mp4'
# time_str1 = get_video_duration(sourceFile)   
# time_str2 ='00:10:00'

print("")
print("")
print(f'指定文件：{sourceFile}')
print(f'文件时长：{time_str1}')
print(f'分割时长：{time_str2}')

proceed = input("是否开始执行？(y/n): ")

if proceed.lower() != 'y':
    print("已取消执行。")
    sys.exit(0)  


# 将用户输入的时间值转换为整数
file_name, file_extension = os.path.splitext(sourceFile)
a= convert_to_seconds(time_str1)
b = convert_to_seconds(time_str2)

c = a // b
remainder = a % b

if remainder != 0:
    c += 1




for i in range(c):
    star = i*b
    end  = (i+1)*b
    se = f"{convert_to_time(star)} ~ {convert_to_time(end)}"
    new_filepath = os.path.join(os.path.dirname(sourceFile), f'{file_name}_{i}' + file_extension)
    ff = ffmpy.FFmpeg(
        executable=ffmpeg_path,
        inputs={sourceFile: None},
        outputs={new_filepath: [
            '-ss', f'{convert_to_time(star)}',
            '-to', f'{convert_to_time(end)}',
            '-c', 'copy'
        ]}
    )
    if remainder != 0 and c== i+1 :
        ff = ffmpy.FFmpeg(
            executable=ffmpeg_path,
            inputs={sourceFile: None},
            outputs={new_filepath: [
                '-ss', f'{convert_to_time(star)}',
                '-c', 'copy'
            ]}
        )
    ff.run()
    # print(f"第 {i+1} 次循环 {se}")
    print(ff.cmd)


print("分割完成！")

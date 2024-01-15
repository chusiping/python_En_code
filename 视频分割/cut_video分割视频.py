import ffmpy
import os

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

sourceFile = input("请输入视频文件：").replace('"', '')
time_str1 = input("请输入视频总时长（格式为 HH:MM:SS）：")
time_str2 = input("请输入第二个时间值（格式为 HH:MM:SS）：")


# 测试用
# sourceFile = r'C:\Users\Administrator\Desktop\新建文件夹\a.mp4'
# time_str1 ='00:48:15'
# time_str2 ='00:10:00'


# 将用户输入的时间值转换为整数
file_name, file_extension = os.path.splitext(sourceFile)
a= convert_to_seconds(time_str1)
b = convert_to_seconds(time_str2)

c = a // b
remainder = a % b

if remainder != 0:
    c += 1


# ffmpeg_path = 'D:\lvse\ffmpeg\bin\ffmpeg.exe'

for i in range(c):
    star = i*b
    end  = (i+1)*b
    se = f"{convert_to_time(star)} ~ {convert_to_time(end)}"
    new_filepath = os.path.join(os.path.dirname(sourceFile), f'{file_name}_{i}' + file_extension)
    ff = ffmpy.FFmpeg(
        inputs={sourceFile: None},
        outputs={new_filepath: [
            '-ss', f'{convert_to_time(star)}',
            '-to', f'{convert_to_time(end)}',
            '-c', 'copy'
        ]}
    )
    if remainder != 0 and c== i+1 :
        ff = ffmpy.FFmpeg(
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

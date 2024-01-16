import subprocess

input_file = input("请输入文件路径（例如：C:\\a\\b.mp4）：")
output_file = input_file.rsplit('.', 1)[0] + '.mp3'

ffmpeg_command = f'ffmpeg.exe -i "{input_file}" -vn "{output_file}"'
print(ffmpeg_command)

subprocess.call(ffmpeg_command, shell=True)

print("转换完成！")
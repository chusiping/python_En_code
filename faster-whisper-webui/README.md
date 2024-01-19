# 这是克隆项目

[持续进化，快速转录，Faster-Whisper对视频进行双语字幕转录实践(Python3.10)](https://www.cnblogs.com/v3ucn/p/17807509.html) 

```

1 参考视频
	E:\____temp\屏幕录制temp存放\自制视频__fast-whisper-large-v2的安装测试.mp4.mp4
	
2 虚拟环境
	python3.11指定版本否则出错
	项目位置 
	E:\git_15home\python_En_code\faster-whisper-webui
	E:\____temp\py\virtualenv_my\Scripts\activate.bat
	
3 模型下载
	https://dl.aifasthub.com/models/guillaumekln/faster-whisper-large-v2
	
	用mklink 映射 E:\git_15home\python_En_code\faster-whisper-webui\models\faster-whisper\large-v2 --> 
				 E:\soft\ai\其他模型__faster-whisper-large-v2
        "E:\git_15home\python_En_code\faster-whisper-webui\models\faster-whisper\large-v2\README.md"
        "E:\git_15home\python_En_code\faster-whisper-webui\models\faster-whisper\large-v2\tokenizer.json"
        "E:\git_15home\python_En_code\faster-whisper-webui\models\faster-whisper\large-v2\vocabulary.txt"
        "E:\git_15home\python_En_code\faster-whisper-webui\models\faster-whisper\large-v2\config.json"
        "E:\git_15home\python_En_code\faster-whisper-webui\models\faster-whisper\large-v2\model.bin"
        
	下载https://github.com/snakers4/silero-vad
		复制silero-vad项目 
		"E:\git_15home\python_En_code\faster-whisper-webui\models\silero-vad\hubconf.py"
        "E:\git_15home\python_En_code\faster-whisper-webui\models\silero-vad\silero-vad.ipynb"
        "E:\git_15home\python_En_code\faster-whisper-webui\models\silero-vad\utils_vad.py"
        "E:\git_15home\python_En_code\faster-whisper-webui\models\silero-vad\examples"
        "E:\git_15home\python_En_code\faster-whisper-webui\models\silero-vad\files"
        
4 CUDA安装
	https://blog.csdn.net/qq_43503670/article/details/119744550
	安装paddlepaddle-gpu
	安装CUDA
	安装cuDNN
	验证PpaddlePaddle-GPU
	
5 测试	
    批处理文件
    @echo off
    chcp 65001 > nul 2>&1
    set /p filename=请输入文件名（带路径）：
    set "filename=%filename:"=%"
    set "command=python cli.py --whisper_implementation faster-whisper --model large-v2 --vad silero-vad --language Chinese --output_dir "E:\____temp\临时存放视频转文字txt用\output" "%filename%""
    echo %command%
    choice /C YN /M "是否要继续执行命令？"
    if errorlevel 2 goto :eof
    start cmd /k "e: && cd E:\git_15home\python_En_code\faster-whisper-webui && E:\____temp\py\virtualenv_my\Scripts\activate.bat && %command%" 
```


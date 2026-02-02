@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUNBUFFERED=1
REM 程序后台执行中，请勿关闭此窗口，可查看run.log
start "" /b python -u task.py --no-send >> run.log 2>&1



@REM start "" /b python main_v2.py ^
@REM   --excel "excle\车充轨迹.xlsx" ^
@REM   --phone 13301110130 ^
@REM   --server-ip 14.23.86.188 ^
@REM   --server-port 6608 ^
@REM   --no-send >> "%LOG_FILE%" 2>&1

@REM tasklist | findstr python
@REM taskkill /F /IM python.exe
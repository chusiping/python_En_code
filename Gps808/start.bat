@REM @echo off
chcp 65001 >nul

REM 获取标准时间 YYYYMMDDhhmmss
for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value') do set dt=%%i

set "LOG_FILE=logs\run_%dt:~0,4%-%dt:~4,2%-%dt:~6,2%_%dt:~8,2%-%dt:~10,2%-%dt:~12,2%.log"

start "" /b python task.py ^
      --no-send >> "%LOG_FILE%" 2>&1

@REM start "" /b python main_v2.py ^
@REM   --excel "excle\车充轨迹.xlsx" ^
@REM   --phone 13301110130 ^
@REM   --server-ip 14.23.86.188 ^
@REM   --server-port 6608 ^
@REM   --no-send >> "%LOG_FILE%" 2>&1

@REM tasklist | findstr python
@REM taskkill /F /IM python.exe
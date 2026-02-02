@echo off
chcp 65001 >nul
cd /e E:\git_15home\python_En_code_git\Gps808

start "" /b python main_v2.py ^
  --excel "excle\车充轨迹.xlsx" ^
  --phone 13301110130 ^
  --server-ip 14.23.86.188 ^
  --server-port 6608 ^
  --no-send >> run.log 2>&1
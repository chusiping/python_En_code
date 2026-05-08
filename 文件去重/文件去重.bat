@echo off
chcp 65001 > nul 2>&1

echo 请输入要扫描的目录路径:
set /p root_dir=
python find_repeatfile.py "%root_dir%"
pause
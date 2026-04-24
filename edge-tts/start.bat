@echo off
chcp 65001 >nul
cd /d %~dp0
start python app.py
timeout /t 5 /nobreak >nul
start http://127.0.0.1:5001

@echo off
chcp 65001 >nul
cd /d %~dp0
start "" python app.py
start http://127.0.0.1:5001
@echo off
echo ========================================
echo   Flask Startup Options
echo ========================================
echo.
set /p ipaddr=Server IP [default: localhost]:
if "%ipaddr%"=="" set ipaddr=localhost

echo   [1] Dev Mode (python app.py)
echo   [2] Production Mode (waitress)
echo   [0] Exit
echo.
echo ========================================

set /p choice=Select (0-2):

if "%choice%"=="1" goto dev
if "%choice%"=="2" goto prod
if "%choice%"=="0" goto end

echo Invalid choice
pause >nul
exit /b

:dev
echo.
echo Starting Dev Mode...
start http://%ipaddr%:7533/B6nM9qW2eR4tY7uI8oP0lK
python app.py
pause >nul
goto end

:prod
echo.
echo Starting Production Mode (Waitress)...
start http://%ipaddr%:7533/B6nM9qW2eR4tY7uI8oP0lK
python -c "from waitress import serve; from app import app; serve(app, host='0.0.0.0', port=7533)"
pause >nul
goto end

:end

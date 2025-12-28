@echo off
chcp 65001 > nul
cls

echo ====================================
echo   Uni Bot - Safe Startup Script
echo ====================================
echo.

REM Kill any existing Python processes to prevent duplicates
echo [1/3] Cleaning up old instances...
taskkill /F /IM python.exe /T >nul 2>&1
timeout /t 1 /nobreak >nul

echo [2/3] Starting bot...
echo.
echo Bot will be available at: http://localhost:8000
echo.
echo ⚠️  IMPORTANT: Do NOT run this script multiple times!
echo              Close this window to stop the bot.
echo.

REM Start the bot
python web_app.py

echo.
echo Bot stopped.
pause

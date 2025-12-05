@echo off
cd /d "%~dp0"
chcp 65001
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
".venv\Scripts\python.exe" web_app.py
pause

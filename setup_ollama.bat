@echo off
echo Starting Ollama service and pulling Gemma 2 model...
echo.

REM Start Ollama service in background
start "" "C:\Users\WIN11\AppData\Local\Programs\Ollama\ollama.exe" serve

REM Wait for service to start
timeout /t 5 /nobreak

REM Pull gemma2 model
echo Pulling Gemma 2 model (this will take a while - ~5GB download)...
"C:\Users\WIN11\AppData\Local\Programs\Ollama\ollama.exe" pull gemma2

echo.
echo Done! Press any key to exit...
pause

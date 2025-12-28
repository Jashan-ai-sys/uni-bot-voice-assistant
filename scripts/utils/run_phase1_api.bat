@echo off
cd /d "%~dp0"
echo Starting Uni RAG Capability API (Phase 1)...
echo access via http://localhost:8000/docs
cd src
"..\.venv\Scripts\python.exe" -m uvicorn api:app --reload
pause

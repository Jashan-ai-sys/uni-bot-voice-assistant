@echo off
echo Starting MCP Agent (Client + Server + LLM)...
echo Type 'exit' to quit.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
"src\..\.venv\Scripts\python.exe" -u src/llm_agent.py
pause

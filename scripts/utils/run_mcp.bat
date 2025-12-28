@echo off
cd /d "c:\Users\WIN11\lpu bot RAG\uni-bot"

set PYTHONPATH=c:\Users\WIN11\lpu bot RAG\uni-bot\src

REM Only redirect stderr to log. Allow stdout to pass through to Claude.
".venv\Scripts\python.exe" src/mcp_server.py 2>> wrapper_log.txt

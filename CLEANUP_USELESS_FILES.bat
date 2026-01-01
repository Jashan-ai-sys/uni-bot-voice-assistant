@echo off
echo ========================================
echo   CLEANUP USELESS FILES
echo ========================================
echo.
echo This will delete all debug/test files
echo Press Ctrl+C to cancel, or
pause

REM Delete debug files
del /Q check_*.py 2>nul
del /Q debug_*.py 2>nul
del /Q test_*.py 2>nul
del /Q verify_*.py 2>nul
del /Q repro*.py 2>nul
del /Q quick_check.py 2>nul

REM Delete JSON fix scripts
del /Q comprehensive_json_fix.py 2>nul
del /Q diagnose_json.py 2>nul
del /Q fix_json*.py 2>nul
del /Q extract_lines.py 2>nul
del /Q find_*.py 2>nul

REM Delete old/backup files
del /Q old_*.py 2>nul
del /Q web_app_backup.py 2>nul

REM Delete utility scripts
del /Q kill_all.py 2>nul
del /Q nuke_port.py 2>nul
del /Q list_models.py 2>nul
del /Q update_icons*.py 2>nul

REM Delete log files
del /Q *.log 2>nul
del /Q *.txt 2>nul

REM Delete test audio
del /Q test_*.wav 2>nul
del /Q test_*.mp3 2>nul
del /Q verify_*.mp3 2>nul

REM Delete empty files
del /Q package.json 2>nul
del /Q package-lock.json 2>nul

REM Delete test folder
rmdir /S /Q tests 2>nul

REM Delete pycache
rmdir /S /Q __pycache__ 2>nul
rmdir /S /Q src\__pycache__ 2>nul

echo.
echo ========================================
echo   CLEANUP COMPLETE!
echo ========================================
echo.
echo Deleted:
echo - All debug/test files
echo - All log files
echo - Old backup files
echo - Test audio files
echo - __pycache__ folders
echo.
pause

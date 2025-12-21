@echo off

if not defined MINIMIZED (
    set MINIMIZED=1
    start "" /min "%~f0"
    exit /b
)

REM Get the directory where the batch file is located
set SCRIPT_DIR=%~dp0

REM Change to that directory
cd /d "%SCRIPT_DIR%"

REM (Optional) Activate your virtual environment if you're using one
REM call C:\path\to\your\env\Scripts\activate

REM Run the Python script - it can be py or python or python3 depending on system and environment
py translate_local_videos.py

REM Pause to see the output in the command window (optional)
REM pause
exit
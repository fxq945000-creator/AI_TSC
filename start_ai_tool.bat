@echo off

REM AI Video Script Analyzer Launcher
REM Double click to run

echo Starting AI Video Script Analyzer...
echo Using Python version: 3.14.0

echo.
REM Set project directory
set PROJECT_DIR=%~dp0

REM Use the correct Python interpreter path
"C:/Users/Administrator/AppData/Local/Programs/Python/Python314/python.exe" "%PROJECT_DIR%main.py"

REM Keep window open for error checking
pause

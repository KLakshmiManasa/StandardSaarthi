@echo off
setlocal
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=venv\Scripts\python.exe"
) else if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    echo [ERROR] Python 3.11 virtual environment not found in venv\ or .venv\.
    echo Please create the virtual environment with Python 3.11 and install requirements before starting.
    exit /b 1
)

if "%HOST%"=="" set HOST=127.0.0.1
if "%PORT%"=="" set PORT=8000

echo Starting StandardSaarthi server on %HOST%:%PORT% using %PYTHON_EXE%...
"%PYTHON_EXE%" -m uvicorn api.routes:app --host %HOST% --port %PORT%

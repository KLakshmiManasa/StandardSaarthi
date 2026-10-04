@echo off
setlocal
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=venv\Scripts\python.exe"
) else if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else if exist "C:\Users\sharlie\AppData\Local\Programs\Python\Python311\python.exe" (
    set "PYTHON_EXE=C:\Users\sharlie\AppData\Local\Programs\Python\Python311\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo Starting StandardSaarthi server using %PYTHON_EXE%...
"%PYTHON_EXE%" -m uvicorn api.routes:app --host 0.0.0.0 --port 8000

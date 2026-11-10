@echo off
REM Creates the venv inside this folder and installs dependencies (Windows).
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.10+ from python.org and tick "Add Python to PATH".
  pause
  exit /b 1
)
if not exist venv python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env copy .env.example .env
echo.
echo Setup finished. Next:
echo   1. Open .env and add your OPENROUTER_API_KEY
echo   2. In the VS Code terminal run: venv\Scripts\Activate.ps1   then   python app.py
pause

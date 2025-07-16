@echo off
echo 🎬 SoulStream Media Server - Windows Starter
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo 📦 Checking Python dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing required packages...
    pip install -r requirements.txt
)

REM Create media directory if it doesn't exist
if not exist "media" mkdir media

REM Start the server
echo 🚀 Starting SoulStream Media Server...
echo 📁 Media directory: %CD%\media
echo 🌐 Server URL: http://localhost:8080
echo.
echo Press Ctrl+C to stop the server
echo.

python server.py --host 127.0.0.1 --port 8080 --upload-folder media

pause 
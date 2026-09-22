@echo off
title BeastClip AI Studio Launcher
color 0b
echo ===================================================
echo           STARTING BEASTCLIP AI STUDIO
echo ===================================================
echo.
cd /d "%~dp0"

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10 or 3.11 from https://www.python.org/downloads/
    echo (Make sure to check "Add Python to PATH" during installation)
    pause
    exit /b 1
)

:: Check if packages are installed (fast check for uvicorn & fastapi)
python -c "import uvicorn, fastapi, faster_whisper, yt_dlp" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] First time setup detected! Installing required dependencies...
    echo This only happens once. Please wait 1-2 minutes...
    python -m pip install -r requirements.txt
)

:: Check if server is already running on port 8000
netstat -ano | findstr :8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] BeastClip AI Server is already running on port 8000.
) else (
    echo [*] Starting BeastClip AI Server on http://127.0.0.1:8000 ...
    start /b python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
    timeout /t 3 /nobreak >nul
)

:: Check if Cloudflare Tunnel is running (optional)
tasklist /fi "imagename eq cloudflared.exe" | findstr cloudflared.exe >nul 2>&1
if %errorlevel% neq 0 (
    if exist "temp\cloudflared.exe" (
        echo [*] Starting Public Share Tunnel in background...
        start /b temp\cloudflared.exe tunnel --url http://127.0.0.1:8000 > temp\cloudflared.log 2>&1
    )
)

echo [*] Opening BeastClip AI in your default browser...
start http://127.0.0.1:8000

echo.
echo ===================================================
echo  BeastClip AI Studio is LIVE at http://127.0.0.1:8000
echo  Closing this launcher in 4 seconds...
echo ===================================================
timeout /t 4 >nul

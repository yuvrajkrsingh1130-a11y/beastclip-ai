@echo off
title BeastClip AI Studio Launcher
color 0b
echo ===================================================
echo           STARTING BEASTCLIP AI STUDIO
echo ===================================================
echo.
cd /d "C:\Users\yuvra\.gemini\antigravity\scratch\beastclip-ai"

:: Check if server is already running on port 8000
netstat -ano | findstr :8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] BeastClip AI Server is already running on port 8000.
) else (
    echo [*] Starting BeastClip AI Server on http://127.0.0.1:8000 ...
    start /b python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
    timeout /t 3 /nobreak >nul
)

:: Check if Cloudflare Tunnel is running
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

@echo off
title BeastClip AI - 1-Click Environment Setup
color 0a
echo =========================================================
echo       BEASTCLIP AI STUDIO - 1-CLICK INSTALLER
echo =========================================================
echo.
cd /d "%~dp0"

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo [*] Attempting to install Python via Windows Package Manager...
    winget install Python.Python.3.11 --silent --accept-source-agreements --accept-package-agreements
    if %errorlevel% neq 0 (
        echo [!] Please manually download & install Python 3.10 or 3.11 from:
        echo     https://www.python.org/downloads/
        echo     (IMPORTANT: Check "Add Python to PATH" during installation)
        pause
        exit /b 1
    )
)
echo [OK] Python is ready.

:: 2. Check FFmpeg
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [*] FFmpeg not found. Automatically installing FFmpeg for high-speed video rendering...
    winget install Gyan.FFmpeg --silent --accept-source-agreements --accept-package-agreements
    if %errorlevel% equ 0 (
        echo [OK] FFmpeg installed successfully!
    ) else (
        echo [NOTICE] If FFmpeg failed to auto-install, you can download it from:
        echo          https://ffmpeg.org/download.html
    )
) else (
    echo [OK] FFmpeg is ready.
)
echo.

:: 3. Install Python Dependencies
echo [*] Installing required Python AI libraries (Whisper, FastAPI, OpenCV, yt-dlp)...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Dependency installation failed! Check your internet connection.
    pause
    exit /b 1
)

echo.
echo =========================================================
echo       [SUCCESS] BeastClip AI is ready to use!
echo =========================================================
echo.
echo You can now launch BeastClip AI anytime by running:
echo   Start_BeastClip_AI.bat
echo.
pause

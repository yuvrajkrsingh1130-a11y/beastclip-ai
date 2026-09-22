@echo off
title BeastClip AI - 1-Click Environment Setup
color 0a
echo =========================================================
echo       BEASTCLIP AI STUDIO - 1-CLICK INSTALLER
echo =========================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10 or 3.11 from https://www.python.org/downloads/
    echo (Make sure to check "Add Python to PATH" during installation)
    pause
    exit /b 1
)
echo [OK] Python detected.

:: 2. Check FFmpeg
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg is not found in PATH!
    echo FFmpeg is required for high-speed video rendering and audio extraction.
    echo Please install FFmpeg (e.g., via 'winget install Gyan.FFmpeg' or from https://ffmpeg.org).
) else (
    echo [OK] FFmpeg detected.
)
echo.

:: 3. Install Python Dependencies
echo [*] Installing required Python libraries...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Dependency installation failed! Check your internet connection or Python setup.
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

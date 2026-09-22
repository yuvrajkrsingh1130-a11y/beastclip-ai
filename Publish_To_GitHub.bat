@echo off
title BeastClip AI - Publish to GitHub
color 0b
echo =========================================================
echo       BEASTCLIP AI STUDIO - PUBLISH TO GITHUB
echo =========================================================
echo.
cd /d "C:\Users\yuvra\.gemini\antigravity\scratch\beastclip-ai"

set "GH_EXE=C:\Program Files\GitHub CLI\gh.exe"

if not exist "%GH_EXE%" (
    echo [*] Installing GitHub CLI...
    winget install --id GitHub.cli --silent --accept-source-agreements --accept-package-agreements
)

echo [*] Checking GitHub authentication...
"%GH_EXE%" auth status >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [*] Please authorize GitHub in the browser window that opens...
    echo.
    "%GH_EXE%" auth login --web --git-protocol https
)

echo.
echo [*] Creating GitHub repository 'beastclip-ai' and uploading code...
"%GH_EXE%" repo create beastclip-ai --public --source=. --remote=origin --push

if %errorlevel% equ 0 (
    echo.
    echo =========================================================
    echo       [SUCCESS] Repository created and published!
    echo =========================================================
    echo.
    "%GH_EXE%" browse
) else (
    echo.
    echo [*] Checking if remote origin already exists, pushing changes...
    git push -u origin main
    "%GH_EXE%" browse
)

echo.
pause

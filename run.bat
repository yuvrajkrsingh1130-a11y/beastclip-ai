@echo off
title BeastClip AI - Automated YouTube Shorts Studio
echo ===================================================
echo     BEASTCLIP AI - LOCAL YOUTUBE SHORTS STUDIO
echo ===================================================
echo.
echo Starting FastAPI Web Server on http://localhost:8000 ...
echo Press Ctrl+C to stop.
echo.

python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
pause

@echo off
title LearnSphere AI - Launch Script
echo ==============================================================
echo       LearnSphere AI: Autonomous Multi-Agent Academic System
echo ==============================================================
echo.

echo Starting Backend Server on http://localhost:8000 ...
start "LearnSphere AI - Backend" cmd /k "cd /d %~dp0backend && .\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server on http://localhost:5173 ...
start "LearnSphere AI - Frontend" cmd /k "cd /d %~dp0frontend && npm run dev -- --host 0.0.0.0 --port 5173"

echo.
echo ==============================================================
echo   LearnSphere AI is running!
echo   Frontend : http://localhost:5173
echo   API Docs : http://localhost:8000/docs
echo   Demo User: demo@learnsphere.ai / password123 (or use 1-Click Demo)
echo ==============================================================
pause

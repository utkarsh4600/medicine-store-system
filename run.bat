@echo off
title PharmaMS - Medicine Store Management System
echo ========================================================
echo   Starting PharmaMS Medicine Store Management System...
echo   Backend Server: Python 3 Standard HTTP & REST Server
echo   Address: http://localhost:8000
echo ========================================================
cd /d "%~dp0"
start "" http://localhost:8000
python backend.py 8000
pause

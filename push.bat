@echo off
title Push Medicine Store System to GitHub
cd /d "%~dp0"
echo ========================================================
echo   Pushing to https://github.com/utkarsh4600/medicine-store-system...
echo ========================================================
git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo [NOTE] Agar authentication prompt aaye ya fail ho, toh pehle:
    echo   gh auth login
    echo run karein, aur fir dobara push.bat chalayein.
) else (
    echo.
    echo ========================================================
    echo   SUCCESSFULLY PUSHED TO GITHUB!
    echo ========================================================
)
pause

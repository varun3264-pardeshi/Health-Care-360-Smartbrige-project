@echo off
title PulsePoint Cyber-Medical OS v6.0 - Live Server
echo ===============================================================================
echo   PULSEPOINT CYBER-MEDICAL INTELLIGENCE OS v6.0 - TERMINAL LIVE LAUNCHER
echo ===============================================================================
echo.
echo [1/2] Checking and freeing Port 8501 if already in use...
powershell -Command "Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
echo [2/2] Starting PulsePoint Control Center Live on http://localhost:8501 ...
echo.
python -m streamlit run ui/app.py --server.port 8501 --client.showSidebarNavigation false
pause

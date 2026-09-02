@echo off
title Master Trading System - Live Terminal
color 0A
echo ============================================================
echo      MASTER TRADING SYSTEM - INDIAN STOCK MARKET
echo ============================================================
echo.
echo [1/2] Checking Python and Dependencies...
cd /d "%~dp0"
echo [2/2] Launching Web Terminal on Port 8501...
echo.
echo ============================================================
echo  TERMINAL RUNNING! Open this URL in your browser:
echo  -> http://localhost:8501
echo  -> Mobile URL (Same Wi-Fi): http://192.168.0.102:8501
echo ============================================================
echo.
echo (Do not close this black window while using the system)
echo.
python -m streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
pause

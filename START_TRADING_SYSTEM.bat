@echo off
title STARTING QUANT CORE TRADING SYSTEM...
color 0A
echo =======================================================
echo    QUANT CORE | PROP-DESK AI TRADING TERMINAL
echo =======================================================
echo.
echo [1/3] Navigating to Project Directory...
cd /d "C:\Users\Shravan\Downloads\TRADING SYSTEM USING AI"

echo [2/3] Checking SQLite Database & Config Integrity...
echo [3/3] Launching Streamlit & Background 3-Level Sentinel...
echo.
echo Opening Browser at http://localhost:8501 ...
start http://localhost:8501

python -m streamlit run app.py --server.headless false --server.port 8501
pause

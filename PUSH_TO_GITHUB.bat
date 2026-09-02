@echo off
title PUSHING CODE TO GITHUB...
color 0B
echo =======================================================
echo    PUSHING QUANT TRADING SYSTEM TO GITHUB
echo =======================================================
echo.
cd /d "C:\Users\Shravan\Downloads\TRADING SYSTEM USING AI"

echo [1/3] Adding Remote URL...
git remote remove origin 2>nul
git remote add origin https://github.com/shravanamburle02-spec/trading-system-ai.git

echo [2/3] Staging and Committing all files...
git add .
git commit -m "Deploy Prop-Desk Quant System to Streamlit Cloud" 2>nul
git branch -M main

echo [3/3] Pushing to GitHub (Sign in if browser popup opens)...
echo.
git push -u origin main

echo.
echo =======================================================
if %ERRORLEVEL% EQU 0 (
    echo SUCCESS: Project successfully pushed to GitHub!
    echo Ab Streamlit Cloud par Deploy button daba sakte ho!
) else (
    echo PUSH FAILED: Please check if repository is created on GitHub.
)
echo =======================================================
echo.
pause

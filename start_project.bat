@echo off
title The Quant Terminal - Startup
echo =======================================================
echo          Starting The Quant Terminal (Next.js)
echo =======================================================

echo [1/3] Spinning up FastAPI Python Backend Engine...
start "Python API Backend" cmd /k "cd /d "%~dp0" && uvicorn src.api:app --reload"

echo [2/3] Spinning up Next.js React Dashboard...
start "Next.js Frontend UI" cmd /k "cd /d "%~dp0\frontend" && npm run dev"

echo [3/3] Waiting for deployment engines to initialize...
:: Delay 5 seconds securely to ensure the local ports bind correctly
timeout /t 5 >nul

echo Launching Default Web Browser organically to your Dashboard!
start http://localhost:3000

echo =======================================================
echo ✅ Application successfully launched across multiple ports!
echo Keep the two new black command prompt windows open actively.
echo =======================================================
exit

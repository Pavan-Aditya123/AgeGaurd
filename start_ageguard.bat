@echo off
echo ============================================================
echo   AgeGuard - Starting Backend + Frontend
echo ============================================================
echo.

:: Kill anything on ports 3000 and 5000
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":3000 " ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":5000 " ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo [1/2] Starting Flask backend (HTTP :5000)...
start "AgeGuard Backend" cmd /k "cd /d %~dp0backend && python app.py"

echo [2/2] Starting React frontend (HTTPS :3000)...
timeout /t 3 /nobreak >nul
start "AgeGuard Frontend" cmd /k "cd /d %~dp0frontend && npm run start:https"

echo.
echo ============================================================
echo   Backend:  http://localhost:5000
echo   Frontend: https://localhost:3000
echo   Network:  https://192.168.40.134:3000
echo.
echo   Wait ~40 seconds for all AI models to load.
echo   Then open https://localhost:3000 in your browser.
echo.
echo   PHONE: Open https://192.168.40.134:3000 first,
echo          tap Advanced, Proceed (one time only).
echo          Then scan the QR code.
echo ============================================================
pause

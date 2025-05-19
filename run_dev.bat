@echo off
REM PyWallet/Prophit - Ambiente de Desenvolvimento Portátil

echo Starting Prophit Development Environment...
echo.

REM Start the Python backend (sempre a partir da pasta do script)
start cmd /k "cd /d %~dp0 && python run.py"

REM Wait a moment to let the backend start
timeout /t 5

REM Start the React frontend (sempre relativo à pasta do script)
start cmd /k "cd /d %~dp0frontend-react && npm run dev"

echo.
echo Development servers are running!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.

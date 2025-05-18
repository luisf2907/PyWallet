@echo off
echo Starting PyWallet Development Environment...
echo.

REM Start the Python backend
start cmd /k "cd /d i:\Github\pywallet3 && python run.py"

REM Wait a moment to let the backend start
timeout /t 5

REM Start the React frontend
start cmd /k "cd /d i:\Github\pywallet3\frontend-react && npm run dev"

echo.
echo Development servers are running!
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.

@echo off
echo.
echo 🛑 Stopping WebWatch Servers...
echo.

echo Stopping Backend Server (Python)...
taskkill /f /im python.exe >nul 2>&1

echo Stopping Frontend Server (Node.js)...
taskkill /f /im node.exe >nul 2>&1

echo.
echo ✅ All WebWatch servers stopped!
pause
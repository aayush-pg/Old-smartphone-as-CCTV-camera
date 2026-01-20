@echo off
echo ========================================
echo   WebWatch Multi-User System Setup
echo ========================================
echo.

echo [1/3] Installing Backend Dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
echo.

echo [2/3] Initializing Multi-User Database...
python setup_db.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)
echo.

echo [3/3] Setup Complete!
echo.
echo ========================================
echo   Multi-User System Ready!
echo ========================================
echo.
echo Default Admin Account:
echo   Username: admin
echo   Password: 123
echo.
echo To start the system:
echo   1. Run: start_backend.bat
echo   2. Run: start_frontend.bat
echo.
echo For more information, see:
echo   MULTI_USER_SYSTEM_GUIDE.md
echo.
pause

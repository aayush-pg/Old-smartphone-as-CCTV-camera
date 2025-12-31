@echo off
echo.
echo ========================================
echo 🎥 WebWatch Live Streaming System
echo ========================================
echo.
echo 🚀 Starting Backend Server...
start "Backend Server" cmd /k "cd /d %~dp0backend && C:\Python314\python.exe app.py"

echo ⏳ Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

echo 🚀 Starting Frontend Server...
start "Frontend Server" cmd /k "cd /d %~dp0WebWatch && npm start"

echo ⏳ Waiting for frontend to compile...
timeout /t 5 /nobreak >nul

echo.
echo ✅ Both servers are starting!
echo 📺 Dashboard: https://localhost:3000
echo 📱 Mobile Camera: https://localhost:3000/broadcast
echo 🔧 Backend API: https://localhost:5001
echo.
echo 📋 Quick Test Instructions:
echo 1. Open Dashboard in main browser
echo 2. Click "Add New Camera" 
echo 3. Copy the 6-digit code
echo 4. Open Mobile page in another tab/device
echo 5. Enter the code and start streaming
echo.
echo Opening Dashboard...
timeout /t 3 /nobreak >nul
start https://localhost:3000

echo.
echo ✅ WebWatch is ready!
echo 🔧 Check browser console (F12) for debugging info
echo 📱 Test with mobile device for best results
pause
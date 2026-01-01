@echo off
echo.
echo ========================================
echo 🔍 Debug Video Pairing System
echo ========================================
echo.

echo 🔧 Starting backend with debug logging...
start "WebWatch Backend Debug" cmd /k "cd /d %~dp0 && call backend\.venv\Scripts\activate && cd backend && python app.py"

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo 🔧 Starting frontend...
start "WebWatch Frontend" cmd /k "cd /d %~dp0WebWatch && npm start"

echo ⏳ Waiting for frontend to compile...
timeout /t 8 /nobreak >nul

echo.
echo ✅ System Started! Debug Instructions:
echo.
echo 📋 Step-by-Step Debug Process:
echo.
echo 1. Dashboard: http://localhost:3000
echo    - Open browser console (F12)
echo    - Click "Add New Camera"
echo    - Watch console for socket events
echo    - Note the 6-digit code generated
echo.
echo 2. Mobile Camera: http://localhost:3000/broadcast
echo    - Open in new tab/device
echo    - Open browser console (F12)
echo    - Enter the 6-digit code
echo    - Watch console for connection events
echo.
echo 3. Backend Terminal:
echo    - Watch for join_room events
echo    - Check room creation logs
echo    - Monitor WebRTC signaling
echo.
echo 🔍 What to Look For:
echo.
echo ❌ Common Issues:
echo - "Room not found" error → Timing issue
echo - "Invalid code" error → Type mismatch
echo - No WebRTC offer → Connection problem
echo - No video → Camera permissions
echo.
echo ✅ Success Indicators:
echo - "join_room_success" events
echo - "room_update" with 2 clients
echo - WebRTC offer/answer exchange
echo - Video element shows stream
echo.

echo Opening Dashboard with console...
start http://localhost:3000

echo.
echo 🔧 Debug Tips:
echo - Check browser console (F12) on both pages
echo - Monitor backend terminal for socket events
echo - Try Chrome browser for best WebRTC support
echo - Ensure camera permissions are granted
echo.
echo 📝 If pairing fails, check:
echo 1. Code type (string vs number)
echo 2. Room creation timing
echo 3. Socket.IO connection status
echo 4. WebRTC offer/answer flow
echo.
pause
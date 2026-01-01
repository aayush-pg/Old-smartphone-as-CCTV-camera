@echo off
echo.
echo ========================================
echo 🎥 Testing FIXED Live Streaming System
echo ========================================
echo.

echo 🔧 Starting backend with fixed signaling...
start "WebWatch Backend FIXED" cmd /k "cd /d %~dp0 && call backend\.venv\Scripts\activate && cd backend && python app.py"

echo ⏳ Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo 🔧 Starting frontend with fixed WebRTC...
start "WebWatch Frontend FIXED" cmd /k "cd /d %~dp0WebWatch && npm start"

echo ⏳ Waiting for frontend to compile...
timeout /t 8 /nobreak >nul

echo.
echo ✅ FIXED System Started! 
echo.
echo 🔧 FIXES APPLIED:
echo ✅ Standardized socket event names (ice-candidate)
echo ✅ Added missing socket event handlers
echo ✅ Improved WebRTC connection handling
echo ✅ Enhanced error logging and debugging
echo ✅ Better mobile camera offer creation
echo ✅ Backward compatibility for old events
echo.
echo 📋 Test Steps:
echo 1. Dashboard: http://localhost:3000
echo 2. Open browser console (F12) - watch for detailed logs
echo 3. Click "Add New Camera" - note the 6-digit code
echo 4. Mobile: http://localhost:3000/broadcast (new tab/device)
echo 5. Open console (F12) - watch connection logs
echo 6. Enter code and allow camera access
echo 7. Video should appear in dashboard within 10 seconds
echo.
echo 🔍 Debug Information:
echo - Dashboard console shows: "✅ WebRTC handshake completed"
echo - Mobile console shows: "🎥 Live streaming connected!"
echo - Backend terminal shows: "Forwarding OFFER/ANSWER"
echo - Video element displays live camera feed
echo.

echo Opening Dashboard...
start http://localhost:3000

echo.
echo 🎯 Expected Results:
echo ✅ Faster pairing (5-10 seconds)
echo ✅ Reliable WebRTC connection
echo ✅ Clear debug logs in console
echo ✅ Automatic fallback if WebRTC fails
echo ✅ Your UI/theme preserved
echo.
echo 🔧 If still not working:
echo 1. Check browser console for specific errors
echo 2. Ensure camera permissions granted
echo 3. Try Chrome browser for best WebRTC support
echo 4. Check that both devices on same network
echo.
pause
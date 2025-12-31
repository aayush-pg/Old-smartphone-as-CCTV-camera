@echo off
echo.
echo 🔍 Testing WebWatch Connection...
echo.

echo Testing Backend Server...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://localhost:5001' -SkipCertificateCheck; Write-Host '✅ Backend: WORKING' -ForegroundColor Green; Write-Host $response.Content } catch { Write-Host '❌ Backend: FAILED' -ForegroundColor Red; Write-Host $_.Exception.Message }"

echo.
echo Testing Frontend Server...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://localhost:3000' -SkipCertificateCheck; Write-Host '✅ Frontend: WORKING' -ForegroundColor Green } catch { Write-Host '❌ Frontend: FAILED' -ForegroundColor Red; Write-Host $_.Exception.Message }"

echo.
echo 📋 If both are working:
echo 📺 Dashboard: https://localhost:3000
echo 📱 Mobile Camera: https://localhost:3000/broadcast
echo.
pause
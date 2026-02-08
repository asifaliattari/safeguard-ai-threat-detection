@echo off
echo ========================================
echo SafeGuard AI - LOCAL ONLY (No ngrok!)
echo By Asif Ali ^& Sharmeen Asif
echo ========================================
echo.
echo Starting backend locally...
echo.

cd backend
start "SafeGuard AI - Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo Waiting for backend to start...
timeout /t 10 >nul

echo.
echo ========================================
echo SUCCESS! Backend is running locally!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Health: http://localhost:8000/health
echo.
echo Now open this in your browser:
echo http://localhost:3000
echo.
echo NOTE: This works ONLY on your computer.
echo If you want online access, use ngrok with paid plan.
echo.
echo Press any key to view logs...
pause >nul

docker-compose logs -f backend 2>nul || echo Backend running in separate window

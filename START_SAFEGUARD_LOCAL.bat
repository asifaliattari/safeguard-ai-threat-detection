@echo off
echo ========================================
echo SafeGuard AI - Local Startup
echo By Asif Ali ^& Sharmeen Asif
echo ========================================
echo.

echo Starting SafeGuard AI locally...
echo.
echo This will start:
echo   - Backend API (http://localhost:8000)
echo   - Frontend (http://localhost:3000)
echo   - PostgreSQL Database
echo   - Redis Cache
echo.

echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running!
    echo.
    echo Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo Docker is running!
echo.

echo Starting all services with Docker Compose...
echo.
docker-compose up -d

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start services
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! SafeGuard AI is running!
echo ========================================
echo.
echo Access your application:
echo.
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo   Health:    http://localhost:8000/health
echo.
echo The backend status indicator will show GREEN when connected!
echo.
echo To view logs:
echo   docker-compose logs -f
echo.
echo To stop:
echo   docker-compose down
echo.
echo Opening frontend in browser...
timeout /t 3 >nul
start http://localhost:3000
echo.
echo Press any key to view logs (Ctrl+C to exit logs)...
pause >nul

docker-compose logs -f

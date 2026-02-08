@echo off
echo ========================================
echo SafeGuard AI - Local Backend + Online Frontend
echo By Asif Ali ^& Sharmeen Asif
echo ========================================
echo.

echo This will:
echo 1. Start backend locally on port 8000
echo 2. Expose it to internet with ngrok
echo 3. Give you a public URL for Vercel frontend
echo.

REM Check if ngrok is installed
where ngrok >nul 2>&1
if errorlevel 1 (
    echo ========================================
    echo STEP 1: Install ngrok
    echo ========================================
    echo.
    echo ngrok is not installed. Please install it:
    echo.
    echo 1. Go to: https://ngrok.com/download
    echo 2. Download ngrok for Windows
    echo 3. Extract ngrok.exe to: C:\Windows\System32
    echo    (or any folder in your PATH)
    echo.
    echo 4. Sign up (free): https://dashboard.ngrok.com/signup
    echo 5. Get your authtoken: https://dashboard.ngrok.com/get-started/your-authtoken
    echo 6. Run: ngrok config add-authtoken YOUR_TOKEN
    echo.
    echo After installing, run this script again!
    echo.
    pause
    exit /b 1
)

echo ========================================
echo STEP 1: Starting Backend
echo ========================================
echo.

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop
    pause
    exit /b 1
)

echo Starting backend with Docker Compose...
docker-compose up -d backend postgres redis

echo Waiting for backend to start (30 seconds)...
timeout /t 30 >nul

echo.
echo ========================================
echo STEP 2: Exposing Backend with ngrok
echo ========================================
echo.

echo Starting ngrok tunnel on port 8000...
echo.
echo KEEP THIS WINDOW OPEN!
echo.

start "ngrok" cmd /k "ngrok http 8000 --log stdout"

timeout /t 5 >nul

echo.
echo ========================================
echo STEP 3: Get Your Public URL
echo ========================================
echo.
echo 1. Look at the ngrok window that just opened
echo 2. Find the line that says "Forwarding"
echo 3. Copy the HTTPS URL (e.g., https://xxxx-xx-xx-xx-xx.ngrok-free.app)
echo.
echo ========================================
echo STEP 4: Update Vercel Frontend
echo ========================================
echo.
echo Run these commands (replace YOUR_NGROK_URL):
echo.
echo   cd frontend
echo   vercel env add NEXT_PUBLIC_API_URL production
echo   [Paste your ngrok HTTPS URL]
echo.
echo   vercel env add NEXT_PUBLIC_WS_URL production
echo   [Paste your ngrok URL with wss:// instead of https://]
echo.
echo   vercel --prod
echo.
echo ========================================
echo Backend is running!
echo ========================================
echo.
echo Local backend: http://localhost:8000
echo Public URL: Check ngrok window
echo.
echo Test health: http://localhost:8000/health
echo.
echo Press any key to view backend logs...
pause >nul

docker-compose logs -f backend

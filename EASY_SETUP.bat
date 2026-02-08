@echo off
echo ========================================
echo SafeGuard AI - SUPER EASY Setup
echo By Asif Ali ^& Sharmeen Asif
echo ========================================
echo.
echo I will do EVERYTHING for you!
echo Just answer a few questions.
echo.

REM Check if ngrok is installed
where ngrok >nul 2>&1
if errorlevel 1 (
    echo ========================================
    echo STEP 1: Install ngrok (ONE TIME ONLY)
    echo ========================================
    echo.
    echo ngrok is not installed. I'll help you install it now!
    echo.
    echo Please do these 3 simple things:
    echo.
    echo 1. Download ngrok:
    echo    Opening download page in your browser...
    timeout /t 2 >nul
    start https://ngrok.com/download
    echo.
    echo 2. After downloading, extract the ZIP file
    echo 3. Move ngrok.exe to: C:\Windows\System32
    echo    (Just drag and drop it there)
    echo.
    echo 4. Sign up (free): https://dashboard.ngrok.com/signup
    echo    Opening signup page...
    timeout /t 2 >nul
    start https://dashboard.ngrok.com/signup
    echo.
    echo 5. After signup, get your token from:
    echo    Opening token page...
    timeout /t 2 >nul
    start https://dashboard.ngrok.com/get-started/your-authtoken
    echo.
    echo After you have your token, type it here:
    set /p NGROK_TOKEN="Paste your ngrok token: "
    echo.
    echo Configuring ngrok...
    ngrok config add-authtoken %NGROK_TOKEN%
    echo.
    echo ✓ ngrok installed and configured!
    echo.
)

echo ========================================
echo STEP 2: Starting Everything
echo ========================================
echo.

REM Check Docker
echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo.
    echo Please start Docker Desktop, then run this script again.
    echo.
    pause
    exit /b 1
)
echo ✓ Docker is running
echo.

echo Starting backend...
docker-compose up -d backend postgres redis
echo ✓ Backend started
echo.

echo Waiting 30 seconds for backend to fully start...
timeout /t 30 >nul

echo Starting ngrok tunnel...
start "ngrok" cmd /c "ngrok http 8000 --log stdout > ngrok.log 2>&1"
echo ✓ ngrok started
echo.

echo Waiting 10 seconds for ngrok to connect...
timeout /t 10 >nul

echo.
echo ========================================
echo STEP 3: Getting Your Public URL
echo ========================================
echo.

REM Try to get ngrok URL from API
echo Fetching ngrok URL automatically...
timeout /t 3 >nul

powershell -Command "$response = Invoke-RestMethod -Uri 'http://localhost:4040/api/tunnels'; $url = $response.tunnels[0].public_url; Write-Host \"Your ngrok URL: $url\"; $url | Out-File -FilePath 'ngrok_url.txt' -Encoding ASCII"

if exist ngrok_url.txt (
    set /p NGROK_URL=<ngrok_url.txt
    echo.
    echo ✓ Got your URL: %NGROK_URL%
    echo.
) else (
    echo.
    echo Could not auto-detect ngrok URL.
    echo.
    echo Please check the ngrok window and copy the HTTPS URL
    echo It looks like: https://xxxx-xx-xx-xx-xx.ngrok-free.app
    echo.
    set /p NGROK_URL="Paste your ngrok URL here: "
    echo.
)

REM Remove https:// for WSS URL
set WSS_URL=%NGROK_URL:https://=wss://%

echo.
echo ========================================
echo STEP 4: Updating Vercel (Automatic!)
echo ========================================
echo.

echo Navigating to frontend...
cd frontend

echo.
echo Removing old environment variables...
call vercel env rm NEXT_PUBLIC_API_URL production --yes 2>nul
call vercel env rm NEXT_PUBLIC_WS_URL production --yes 2>nul

echo.
echo Setting new API URL...
echo %NGROK_URL%| vercel env add NEXT_PUBLIC_API_URL production

echo.
echo Setting new WebSocket URL...
echo %WSS_URL%| vercel env add NEXT_PUBLIC_WS_URL production

echo.
echo Deploying to Vercel...
call vercel --prod

cd ..

echo.
echo ========================================
echo ✓ DONE! Everything is ready!
echo ========================================
echo.
echo Your backend is running at: %NGROK_URL%
echo Your frontend is at: https://frontend-beige-kappa-38.vercel.app
echo.
echo Open your frontend and the status should show GREEN!
echo.
echo IMPORTANT: Keep this window open!
echo If you close it, the ngrok tunnel will stop.
echo.
echo To view logs, press any key...
pause >nul

docker-compose logs -f backend

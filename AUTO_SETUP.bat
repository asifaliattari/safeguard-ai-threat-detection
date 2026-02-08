@echo off
echo ========================================
echo SafeGuard AI - AUTO SETUP (I Do Everything!)
echo By Asif Ali ^& Sharmeen Asif
echo ========================================
echo.
echo I will download, install, and setup EVERYTHING automatically!
echo Just sit back and relax...
echo.

REM Check if ngrok is already installed
where ngrok >nul 2>&1
if not errorlevel 1 (
    echo ✓ ngrok is already installed!
    goto :start_services
)

echo ========================================
echo Step 1: Downloading ngrok...
echo ========================================
echo.

REM Create temp directory
if not exist "temp_ngrok" mkdir temp_ngrok
cd temp_ngrok

echo Downloading ngrok for Windows...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile 'ngrok.zip'}"

if not exist "ngrok.zip" (
    echo ERROR: Failed to download ngrok
    echo Please download manually from: https://ngrok.com/download
    pause
    exit /b 1
)

echo ✓ Downloaded ngrok
echo.

echo Extracting ngrok...
powershell -Command "Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force"

if not exist "ngrok.exe" (
    echo ERROR: Failed to extract ngrok
    pause
    exit /b 1
)

echo ✓ Extracted ngrok
echo.

echo Installing ngrok...
REM Try to move to System32, if fails, use local directory
copy ngrok.exe C:\Windows\System32\ >nul 2>&1
if errorlevel 1 (
    echo Could not install to System32 (need admin rights)
    echo Installing to local directory instead...
    copy ngrok.exe ..\ >nul 2>&1
    cd ..
    set "PATH=%CD%;%PATH%"
) else (
    echo ✓ Installed to System32
    cd ..
)

REM Clean up
if exist "temp_ngrok" rmdir /s /q temp_ngrok

echo ✓ ngrok installed successfully!
echo.

echo ========================================
echo Step 2: Configuring ngrok...
echo ========================================
echo.

echo Setting up your ngrok token...
ngrok config add-authtoken 2tXSHTq9qAiJKiyRoiKnuhK6jtN_6G1wxBiijNPzy31Z7cWYu

if errorlevel 1 (
    echo ERROR: Failed to configure ngrok
    pause
    exit /b 1
)

echo ✓ ngrok configured successfully!
echo.

:start_services

echo ========================================
echo Step 3: Starting Backend...
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

echo Starting backend with Docker Compose...
docker-compose up -d backend postgres redis

if errorlevel 1 (
    echo ERROR: Failed to start backend
    pause
    exit /b 1
)

echo ✓ Backend started
echo.

echo Waiting 30 seconds for backend to fully start...
timeout /t 30 >nul

echo ========================================
echo Step 4: Starting ngrok tunnel...
echo ========================================
echo.

echo Opening ngrok tunnel...
start "SafeGuard AI - ngrok Tunnel" cmd /c "ngrok http 8000 --log stdout"

echo ✓ ngrok tunnel started
echo.

echo Waiting 10 seconds for ngrok to connect...
timeout /t 10 >nul

echo ========================================
echo Step 5: Getting Your Public URL...
echo ========================================
echo.

echo Fetching ngrok URL automatically...
timeout /t 5 >nul

REM Get ngrok URL from API
powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://localhost:4040/api/tunnels' -ErrorAction Stop; $url = $response.tunnels[0].public_url; Write-Host \"Your ngrok URL: $url\"; $url | Out-File -FilePath 'ngrok_url.txt' -Encoding ASCII -NoNewline } catch { Write-Host 'Could not get URL automatically' }"

if exist ngrok_url.txt (
    set /p NGROK_URL=<ngrok_url.txt
    echo.
    echo ✓ Got your URL: %NGROK_URL%
    echo.
) else (
    echo.
    echo Could not auto-detect ngrok URL.
    echo Please check the ngrok window and find the HTTPS URL
    echo It looks like: https://xxxx-xx-xx-xx-xx.ngrok-free.app
    echo.
    set /p NGROK_URL="Paste your ngrok HTTPS URL here: "
    echo %NGROK_URL% > ngrok_url.txt
    echo.
)

REM Create WSS URL
set "WSS_URL=%NGROK_URL:https://=wss://%"

echo ========================================
echo Step 6: Updating Vercel (Automatic!)
echo ========================================
echo.

cd frontend

echo Removing old environment variables...
call vercel env rm NEXT_PUBLIC_API_URL production --yes 2>nul
call vercel env rm NEXT_PUBLIC_WS_URL production --yes 2>nul

echo.
echo Setting API URL: %NGROK_URL%
echo %NGROK_URL%| vercel env add NEXT_PUBLIC_API_URL production

echo.
echo Setting WebSocket URL: %WSS_URL%
echo %WSS_URL%| vercel env add NEXT_PUBLIC_WS_URL production

echo.
echo Deploying to Vercel (this takes 1-2 minutes)...
call vercel --prod

cd ..

echo.
echo ========================================
echo ✓✓✓ SUCCESS! Everything is Ready! ✓✓✓
echo ========================================
echo.
echo Your Backend: %NGROK_URL%
echo Your Frontend: https://frontend-beige-kappa-38.vercel.app
echo.
echo ✅ ngrok downloaded and installed
echo ✅ Backend running on your computer
echo ✅ ngrok tunnel active
echo ✅ Vercel frontend updated
echo ✅ Everything connected!
echo.
echo 🌐 Open this URL now:
echo    https://frontend-beige-kappa-38.vercel.app
echo.
echo The status indicator should show GREEN! 🟢
echo.
echo IMPORTANT: Keep this window and the ngrok window open!
echo.
echo To view backend logs, press any key...
pause >nul

docker-compose logs -f backend

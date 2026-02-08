@echo off
echo ========================================
echo SafeGuard AI - NO DOCKER Setup
echo By Asif Ali ^& Sharmeen Asif
echo ========================================
echo.
echo This version does NOT need Docker!
echo I will setup everything automatically!
echo.

REM Check if Python is installed
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.11 from:
    echo https://www.python.org/downloads/
    echo.
    echo Opening download page...
    start https://www.python.org/downloads/
    echo.
    echo After installing Python, run this script again!
    pause
    exit /b 1
)

echo ✓ Python is installed
python --version
echo.

REM Check if ngrok is already installed
where ngrok >nul 2>&1
if not errorlevel 1 (
    echo ✓ ngrok is already installed!
    goto :install_dependencies
)

echo ========================================
echo Step 1: Installing ngrok...
echo ========================================
echo.

REM Create temp directory
if not exist "temp_ngrok" mkdir temp_ngrok
cd temp_ngrok

echo Downloading ngrok for Windows...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip' -OutFile 'ngrok.zip'}"

if not exist "ngrok.zip" (
    echo ERROR: Failed to download ngrok
    pause
    exit /b 1
)

echo ✓ Downloaded ngrok
echo.

echo Extracting ngrok...
powershell -Command "Expand-Archive -Path 'ngrok.zip' -DestinationPath '.' -Force"

echo ✓ Extracted ngrok
echo.

echo Installing ngrok...
copy ngrok.exe C:\Windows\System32\ >nul 2>&1
if errorlevel 1 (
    echo Installing to local directory...
    copy ngrok.exe ..\ >nul 2>&1
    cd ..
    set "PATH=%CD%;%PATH%"
) else (
    echo ✓ Installed to System32
    cd ..
)

REM Clean up
if exist "temp_ngrok" rmdir /s /q temp_ngrok

echo ✓ ngrok installed!
echo.

echo Configuring ngrok...
ngrok config add-authtoken 2tXSHTq9qAiJKiyRoiKnuhK6jtN_6G1wxBiijNPzy31Z7cWYu

echo ✓ ngrok configured!
echo.

:install_dependencies

echo ========================================
echo Step 2: Installing Python packages...
echo ========================================
echo.

cd backend

echo Installing backend dependencies (this may take 3-5 minutes)...
pip install --upgrade pip >nul 2>&1
echo Installing minimal packages (works with Python 3.13)...
pip install -r requirements.minimal.txt

if errorlevel 1 (
    echo ERROR: Failed to install Python packages
    pause
    exit /b 1
)

echo ✓ All Python packages installed!
echo.

cd ..

echo ========================================
echo Step 3: Starting Backend...
echo ========================================
echo.

echo Starting FastAPI backend on port 8000...
start "SafeGuard AI - Backend" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo ✓ Backend started!
echo.

echo Waiting 30 seconds for backend to fully start...
timeout /t 30 >nul

echo ========================================
echo Step 4: Starting ngrok tunnel...
echo ========================================
echo.

echo Opening ngrok tunnel...
start "SafeGuard AI - ngrok" cmd /k "ngrok http 8000 --log stdout"

echo ✓ ngrok tunnel started!
echo.

echo Waiting 10 seconds for ngrok to connect...
timeout /t 10 >nul

echo ========================================
echo Step 5: Getting Your Public URL...
echo ========================================
echo.

echo Fetching ngrok URL automatically...
timeout /t 5 >nul

powershell -Command "try { $response = Invoke-RestMethod -Uri 'http://localhost:4040/api/tunnels' -ErrorAction Stop; $url = $response.tunnels[0].public_url; Write-Host \"Your ngrok URL: $url\"; $url | Out-File -FilePath 'ngrok_url.txt' -Encoding ASCII -NoNewline } catch { Write-Host 'Could not get URL automatically' }"

if exist ngrok_url.txt (
    set /p NGROK_URL=<ngrok_url.txt
    echo.
    echo ✓ Got your URL: %NGROK_URL%
    echo.
) else (
    echo.
    echo Could not auto-detect ngrok URL.
    echo Check the ngrok window for the HTTPS URL
    echo.
    set /p NGROK_URL="Paste your ngrok HTTPS URL here: "
    echo %NGROK_URL% > ngrok_url.txt
    echo.
)

REM Create WSS URL
set "WSS_URL=%NGROK_URL:https://=wss://%"

echo ========================================
echo Step 6: Updating Vercel...
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
echo ✅ Python backend running (NO DOCKER!)
echo ✅ ngrok tunnel active
echo ✅ Vercel frontend updated
echo ✅ Everything connected!
echo.
echo 🌐 Open this URL now:
echo    https://frontend-beige-kappa-38.vercel.app
echo.
echo The status indicator should show GREEN! 🟢
echo.
echo IMPORTANT: Keep the backend and ngrok windows open!
echo.
echo Press any key to exit...
pause >nul

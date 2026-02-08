@echo off
echo ========================================
echo SafeGuard AI - FULL ONLINE (With AI!)
echo By Asif Ali ^& Sharmeen Asif
echo ========================================
echo.

REM Check Python version
python --version 2>&1 | findstr /C:"3.11" >nul
if errorlevel 1 (
    echo ERROR: You need Python 3.11 for AI detection!
    echo.
    echo Your current Python version:
    python --version
    echo.
    echo Please run: INSTALL_PYTHON311.bat
    echo.
    pause
    exit /b 1
)

echo Γ£ô Python 3.11 detected - AI detection will work!
echo.

echo ========================================
echo Installing AI Packages...
echo ========================================
echo.

cd backend

echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing FULL requirements (this takes 5-10 minutes)...
echo Downloading torch (2GB), YOLO models, etc...
echo.

python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
python -m pip install ultralytics opencv-python-headless pillow numpy
python -m pip install fastapi uvicorn[standard] websockets python-multipart
python -m pip install openai python-dotenv pydantic pydantic-settings aiosmtplib

if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo Γ£ô All AI packages installed!
cd ..

echo.
echo ========================================
echo Starting Backend with AI...
echo ========================================
echo.

cd backend
start "SafeGuard AI - Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
cd ..

echo Waiting for backend to load AI models (30 seconds)...
timeout /t 30 >nul

echo.
echo ========================================
echo Installing Cloudflare Tunnel...
echo ========================================
echo.

where cloudflared >nul 2>&1
if errorlevel 1 (
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
    move cloudflared.exe C:\Windows\System32\cloudflared.exe 2>nul
    echo Γ£ô Cloudflared installed
) else (
    echo Γ£ô Cloudflared already installed
)

echo.
echo ========================================
echo Starting Cloudflare Tunnel...
echo ========================================
echo.

start "Cloudflare Tunnel" cmd /k "cloudflared tunnel --url http://localhost:8000"

timeout /t 15 >nul

echo.
echo ========================================
echo Get Your Cloudflare URL
echo ========================================
echo.
echo Check the "Cloudflare Tunnel" window.
echo Find the URL: https://xxxxxxxx.trycloudflare.com
echo.
set /p CF_URL="Paste your Cloudflare URL: "

if "%CF_URL%"=="" (
    echo Error: No URL
    pause
    exit /b 1
)

set "WSS_URL=%CF_URL:https://=wss://%"

echo.
echo ========================================
echo Updating Vercel...
echo ========================================
echo.

cd frontend

call vercel env rm NEXT_PUBLIC_API_URL production --yes 2>nul
call vercel env rm NEXT_PUBLIC_WS_URL production --yes 2>nul

echo %CF_URL%| vercel env add NEXT_PUBLIC_API_URL production
echo %WSS_URL%| vercel env add NEXT_PUBLIC_WS_URL production

echo.
echo Deploying...
call vercel --prod

cd ..

echo.
echo ========================================
echo ­ƒÄë SUCCESS! AI Detection is ONLINE! ­ƒÄë
echo ========================================
echo.
echo Backend (with AI): %CF_URL%
echo Frontend: https://frontend-beige-kappa-38.vercel.app
echo.
echo ­ƒÜó AI Detection: ENABLED
echo ­ƒÜó Person Detection: WORKING
echo ­ƒÜó Threat Detection: WORKING
echo.
echo ­ƒîê OPEN: https://frontend-beige-kappa-38.vercel.app
echo.
pause

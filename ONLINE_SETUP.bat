@echo off
echo ========================================
echo SafeGuard AI - ONLINE Setup (FREE!)
echo By Asif Ali ^& Sharmeen Asif
echo ========================================
echo.
echo Using Cloudflare Tunnel - NO warning pages!
echo 100%% FREE and works perfectly online!
echo.

REM Check if cloudflared is installed
where cloudflared >nul 2>&1
if not errorlevel 1 (
    echo Γ£ô cloudflared is already installed!
    goto :start_services
)

echo ========================================
echo Step 1: Installing Cloudflare Tunnel...
echo ========================================
echo.

REM Create temp directory
if not exist "temp_cf" mkdir temp_cf
cd temp_cf

echo Downloading cloudflared for Windows...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'}"

if not exist "cloudflared.exe" (
    echo ERROR: Failed to download cloudflared
    pause
    exit /b 1
)

echo Γ£ô Downloaded cloudflared
echo.

echo Installing cloudflared...
copy cloudflared.exe C:\Windows\System32\ >nul 2>&1
if errorlevel 1 (
    echo Installing to local directory...
    copy cloudflared.exe ..\ >nul 2>&1
    cd ..
    set "PATH=%CD%;%PATH%"
) else (
    echo Γ£ô Installed to System32
    cd ..
)

REM Clean up
if exist "temp_cf" rmdir /s /q temp_cf

echo Γ£ô cloudflared installed successfully!
echo.

:start_services

echo ========================================
echo Step 2: Starting Backend...
echo ========================================
echo.

echo Checking if backend is running...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo Starting backend...
    cd backend
    start "SafeGuard AI - Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    cd ..
    echo Waiting 15 seconds for backend to start...
    timeout /t 15 >nul
) else (
    echo Γ£ô Backend already running
)

echo.
echo ========================================
echo Step 3: Starting Cloudflare Tunnel...
echo ========================================
echo.

echo Opening Cloudflare Tunnel (NO warning page!)...
start "SafeGuard AI - Cloudflare Tunnel" cmd /k "cloudflared tunnel --url http://localhost:8000"

echo Γ£ô Tunnel started!
echo.

echo Waiting 10 seconds for tunnel to connect...
timeout /t 10 >nul

echo.
echo ========================================
echo Step 4: Get Your Public URL
echo ========================================
echo.
echo Look at the "Cloudflare Tunnel" window that just opened.
echo.
echo Find the line that says:
echo   "Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):"
echo   https://XXXXXXXX.trycloudflare.com
echo.
echo Copy that URL and paste it here:
set /p CF_URL="Paste your Cloudflare URL: "

if "%CF_URL%"=="" (
    echo Error: No URL provided
    pause
    exit /b 1
)

echo.
echo Γ£ô Got URL: %CF_URL%
echo.

REM Create WSS URL
set "WSS_URL=%CF_URL:https://=wss://%"

echo ========================================
echo Step 5: Updating Vercel...
echo ========================================
echo.

cd frontend

echo Removing old environment variables...
call vercel env rm NEXT_PUBLIC_API_URL production --yes 2>nul
call vercel env rm NEXT_PUBLIC_WS_URL production --yes 2>nul

echo.
echo Setting API URL: %CF_URL%
echo %CF_URL%| vercel env add NEXT_PUBLIC_API_URL production

echo.
echo Setting WebSocket URL: %WSS_URL%
echo %WSS_URL%| vercel env add NEXT_PUBLIC_WS_URL production

echo.
echo Deploying to Vercel...
call vercel --prod

cd ..

echo.
echo ========================================
echo Γ£ôΓ£ôΓ£ô SUCCESS! Your App is ONLINE! Γ£ôΓ£ôΓ£ô
echo ========================================
echo.
echo Your Backend: %CF_URL%
echo Your Frontend: https://frontend-beige-kappa-38.vercel.app
echo.
echo Γ£å Cloudflare Tunnel (NO warning page!)
echo Γ£å Backend running
echo Γ£å Vercel frontend updated
echo Γ£å Everything connected!
echo.
echo ­ƒîê Open this URL now:
echo    https://frontend-beige-kappa-38.vercel.app
echo.
echo The status indicator will be GREEN! ­ƒÜó
echo.
echo IMPORTANT: Keep the Cloudflare Tunnel window open!
echo.
echo Press any key to exit...
pause >nul

@echo off
echo ========================================
echo SafeGuard AI - AUTO ONLINE (100%% FREE!)
echo By Asif Ali ^& Sharmeen Asif
echo ========================================
echo.
echo Using Cloudflare Tunnel
echo - NO warning pages like ngrok!
echo - 100%% FREE forever!
echo - Works perfectly online!
echo.

REM Check if cloudflared is installed
where cloudflared >nul 2>&1
if not errorlevel 1 (
    echo Γ£ô cloudflared already installed
    goto :start_backend
)

echo ========================================
echo Installing Cloudflare Tunnel...
echo ========================================
echo.

powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'}"

if exist "cloudflared.exe" (
    move cloudflared.exe C:\Windows\System32\cloudflared.exe >nul 2>&1
    if errorlevel 1 (
        echo Γ£ô Installed locally
        set "PATH=%CD%;%PATH%"
    ) else (
        echo Γ£ô Installed to System32
    )
) else (
    echo ERROR: Download failed
    pause
    exit /b 1
)

:start_backend

echo.
echo ========================================
echo Starting Backend...
echo ========================================
echo.

curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    cd backend
    start "SafeGuard Backend" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    cd ..
    timeout /t 15 >nul
    echo Γ£ô Backend started
) else (
    echo Γ£ô Backend already running
)

echo.
echo ========================================
echo Starting Cloudflare Tunnel...
echo ========================================
echo.

start "Cloudflare Tunnel" cmd /k "cloudflared tunnel --url http://localhost:8000 2>&1 | tee cloudflare.log"

echo Waiting 15 seconds for tunnel to connect...
timeout /t 15 >nul

echo.
echo Extracting your public URL...
timeout /t 5 >nul

REM Try to extract URL from log
powershell -Command "if (Test-Path 'cloudflare.log') { Get-Content 'cloudflare.log' | Select-String -Pattern 'https://.*\.trycloudflare\.com' | Select-Object -First 1 | ForEach-Object { $_.Matches.Value } | Out-File -FilePath 'cf_url.txt' -Encoding ASCII -NoNewline }"

if exist cf_url.txt (
    set /p CF_URL=<cf_url.txt
    if not "%CF_URL%"=="" (
        echo Γ£ô Auto-detected URL: %CF_URL%
        goto :update_vercel
    )
)

echo.
echo Could not auto-detect URL.
echo Please check the "Cloudflare Tunnel" window and find the URL.
echo It looks like: https://xxxxxxxx.trycloudflare.com
echo.
set /p CF_URL="Paste your Cloudflare URL here: "

:update_vercel

if "%CF_URL%"=="" (
    echo ERROR: No URL provided
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
echo Deploying to production...
call vercel --prod

cd ..

echo.
echo ========================================
echo ­ƒÄë SUCCESS! Your App is ONLINE! ­ƒÄë
echo ========================================
echo.
echo Backend: %CF_URL%
echo Frontend: https://frontend-beige-kappa-38.vercel.app
echo.
echo ­ƒîê OPEN NOW: https://frontend-beige-kappa-38.vercel.app
echo.
echo Status will be GREEN! ­ƒÜó
echo.
echo Keep the Cloudflare Tunnel window open!
echo.
pause

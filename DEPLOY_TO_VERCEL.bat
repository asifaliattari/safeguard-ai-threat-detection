@echo off
echo ========================================
echo SafeGuard AI - Vercel Deployment
echo By Asif Ali ^& Sharmeen Asif
echo ========================================
echo.

REM Get backend URL
set /p HF_USERNAME="Enter your Hugging Face username: "

set BACKEND_URL=https://%HF_USERNAME%-safeguard-ai-backend.hf.space
set WS_URL=wss://%HF_USERNAME%-safeguard-ai-backend.hf.space

echo.
echo Frontend will connect to:
echo Backend API: %BACKEND_URL%
echo WebSocket: %WS_URL%
echo.

pause

echo.
echo Checking Vercel CLI...
where vercel >nul 2>&1
if errorlevel 1 (
    echo Vercel CLI not found. Installing...
    npm install -g vercel
)

echo.
echo Logging into Vercel...
echo A browser window will open. Please login.
echo.
vercel login

if errorlevel 1 (
    echo.
    echo ERROR: Failed to login to Vercel
    pause
    exit /b 1
)

echo.
echo Deploying frontend to Vercel...
cd frontend

echo.
echo Setting environment variables...
echo %BACKEND_URL% | vercel env add NEXT_PUBLIC_API_URL production
echo %WS_URL% | vercel env add NEXT_PUBLIC_WS_URL production

echo.
echo Deploying to production...
vercel --prod --yes

if errorlevel 1 (
    echo.
    echo ERROR: Deployment failed
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo ========================================
echo SUCCESS! Frontend deployed to Vercel
echo ========================================
echo.
echo Your frontend is now live!
echo Check your Vercel dashboard for the URL:
echo https://vercel.com/dashboard
echo.
echo Test your deployment:
echo 1. Open your Vercel URL
echo 2. Click "Start AI Detection"
echo 3. Allow camera access
echo 4. Test threat detection
echo.
echo Team: Asif Ali ^& Sharmeen Asif
echo ========================================
echo.

pause

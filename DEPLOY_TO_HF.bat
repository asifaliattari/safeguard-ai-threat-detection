@echo off
echo ========================================
echo SafeGuard AI - Hugging Face Deployment
echo By Asif Ali ^& Sharmeen Asif
echo ========================================
echo.

REM Get user inputs
set /p HF_USERNAME="Enter your Hugging Face username: "
set /p HF_TOKEN="Enter your Hugging Face token (will be hidden): "

echo.
echo Space will be created at:
echo https://huggingface.co/spaces/%HF_USERNAME%/safeguard-ai-backend
echo.
echo Backend URL will be:
echo https://%HF_USERNAME%-safeguard-ai-backend.hf.space
echo.

pause

echo.
echo Cloning Hugging Face Space...
git clone https://%HF_USERNAME%:%HF_TOKEN%@huggingface.co/spaces/%HF_USERNAME%/safeguard-ai-backend hf-deploy-temp

if errorlevel 1 (
    echo.
    echo ERROR: Failed to clone Space. Please check:
    echo 1. You created the Space at https://huggingface.co/new-space
    echo 2. Space name is: safeguard-ai-backend
    echo 3. Your username and token are correct
    echo.
    pause
    exit /b 1
)

echo.
echo Copying backend files...
xcopy /E /I /Y backend\* hf-deploy-temp\
copy /Y backend\Dockerfile hf-deploy-temp\Dockerfile

echo.
echo Creating README.md...
(
echo ---
echo title: SafeGuard AI Backend
echo emoji: 🛡️
echo colorFrom: blue
echo colorTo: cyan
echo sdk: docker
echo pinned: false
echo ---
echo.
echo # SafeGuard AI - Threat Detection Backend
echo.
echo **Developed by Asif Ali ^& Sharmeen Asif**
echo.
echo Real-time humanitarian threat detection API powered by YOLOv8, MediaPipe, and OpenAI.
echo.
echo ## Features
echo.
echo - 🎯 YOLOv8 object detection
echo - 👤 Activity recognition
echo - 🤖 AI analysis with GPT-4
echo - 📧 Multi-channel alerts
echo - 🌊 WebSocket real-time detection
echo.
echo ## API
echo.
echo - GET /health - Health check
echo - GET /docs - API documentation
echo - WebSocket /ws/detect/{user_id} - Real-time detection
echo.
echo ## Authors
echo.
echo - **Asif Ali** - Lead Developer ^& AI Engineer
echo - **Sharmeen Asif** - Co-Developer ^& System Architect
echo.
echo GitHub: https://github.com/asifaliattari/safeguard-ai-threat-detection
echo.
echo MIT License - Copyright (c^) 2025 Asif Ali ^& Sharmeen Asif
) > hf-deploy-temp\README.md

echo.
echo Committing and pushing to Hugging Face...
cd hf-deploy-temp
git add .
git commit -m "Deploy SafeGuard AI Backend by Asif Ali & Sharmeen Asif"
git push origin main

if errorlevel 1 (
    echo.
    echo ERROR: Failed to push to Hugging Face
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo ========================================
echo SUCCESS! Backend deployed to Hugging Face
echo ========================================
echo.
echo Your backend is building at:
echo https://huggingface.co/spaces/%HF_USERNAME%/safeguard-ai-backend
echo.
echo API URL (once built):
echo https://%HF_USERNAME%-safeguard-ai-backend.hf.space
echo.
echo Health check:
echo https://%HF_USERNAME%-safeguard-ai-backend.hf.space/health
echo.
echo API Docs:
echo https://%HF_USERNAME%-safeguard-ai-backend.hf.space/docs
echo.
echo Building takes 5-10 minutes. Monitor logs in the Space.
echo.
echo IMPORTANT: Configure these secrets in Space Settings:
echo - OPENAI_API_KEY
echo - EMAIL_FROM
echo - EMAIL_PASSWORD
echo - EMAIL_TO
echo - SMTP_HOST=smtp.gmail.com
echo - SMTP_PORT=587
echo.
echo Next: Run DEPLOY_TO_VERCEL.bat to deploy frontend
echo.

REM Cleanup
rmdir /S /Q hf-deploy-temp 2>nul

pause

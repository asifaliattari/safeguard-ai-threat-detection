@echo off
echo 🚀 SafeGuard AI - Quick Start
echo ==============================
echo.

cd frontend

echo 📦 Installing frontend dependencies...
call npm install

echo.
echo 🗄️  Setting up database...
call npx prisma generate
call npx prisma db push

echo.
echo ✅ Setup complete!
echo.
echo 📝 Next steps:
echo 1. Edit frontend\.env.local with your API keys
echo 2. Edit backend\.env with your API keys
echo 3. Open TWO terminals:
echo.
echo Terminal 1 (Backend):
echo   cd backend
echo   venv\Scripts\activate
echo   pip install anthropic aiohttp aiosmtplib
echo   python -m uvicorn app.main:app --reload
echo.
echo Terminal 2 (Frontend):
echo   cd frontend
echo   npm run dev
echo.
echo 🎉 Then open http://localhost:3000
pause

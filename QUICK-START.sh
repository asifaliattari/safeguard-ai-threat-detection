#!/bin/bash
# Quick Start Script for SafeGuard AI
# Run after getting API keys

echo "🚀 SafeGuard AI - Quick Start"
echo "=============================="
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ] && [ ! -f "frontend/package.json" ]; then
    echo "❌ Please run this from the project root directory"
    exit 1
fi

# Navigate to frontend
cd frontend

echo "📦 Step 1: Installing frontend dependencies..."
npm install

echo ""
echo "🗄️  Step 2: Setting up database..."
npx prisma generate
npx prisma db push

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit frontend/.env.local with your API keys"
echo "2. Edit backend/.env with your API keys"
echo "3. Run: cd backend && pip install -r requirements.txt"
echo "4. Start backend: cd backend && python -m uvicorn app.main:app --reload"
echo "5. Start frontend: cd frontend && npm run dev"
echo ""
echo "🎉 Then open http://localhost:3000"

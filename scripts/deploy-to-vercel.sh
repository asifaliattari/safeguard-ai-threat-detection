#!/bin/bash

# SafeGuard AI - Vercel Deployment Script
# Deploy frontend to Vercel

set -e

echo "▲ SafeGuard AI - Vercel Deployment"
echo "===================================="
echo ""

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI is not installed"
    echo "Install it with: npm install -g vercel"
    exit 1
fi

# Navigate to frontend
cd frontend

# Check if logged in
if ! vercel whoami &> /dev/null; then
    echo "❌ Not logged in to Vercel"
    echo "Run: vercel login"
    exit 1
fi

echo "✅ Logged in to Vercel as: $(vercel whoami)"
echo ""

# Get backend URL
echo "Enter your Hugging Face backend URL (e.g., https://username-spacename.hf.space):"
read -r BACKEND_URL

# Remove trailing slash
BACKEND_URL="${BACKEND_URL%/}"

# Convert http to ws for WebSocket
WS_URL=$(echo "$BACKEND_URL" | sed 's/https:/wss:/')

echo ""
echo "📋 Configuration:"
echo "  Backend API: $BACKEND_URL"
echo "  WebSocket: $WS_URL"
echo ""

# Set environment variables
echo "⚙️  Setting environment variables..."
vercel env add NEXT_PUBLIC_API_URL production <<< "$BACKEND_URL"
vercel env add NEXT_PUBLIC_WS_URL production <<< "$WS_URL"

echo "✅ Environment variables set"
echo ""

# Deploy
echo "🚀 Deploying to Vercel production..."
DEPLOYMENT_URL=$(vercel --prod --yes)

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Your Frontend:"
echo "  URL: $DEPLOYMENT_URL"
echo ""
echo "🧪 Testing..."
sleep 5

# Test health
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$DEPLOYMENT_URL" || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Frontend is healthy!"
else
    echo "⚠️  Frontend health check returned: HTTP $HTTP_CODE"
fi

echo ""
echo "🔧 Next steps:"
echo "  1. Open: $DEPLOYMENT_URL"
echo "  2. Click 'Start AI Detection'"
echo "  3. Allow camera permissions"
echo "  4. Test threat detection with objects"
echo "  5. Test AI chatbot"
echo ""
echo "📊 Vercel Dashboard: https://vercel.com/dashboard"

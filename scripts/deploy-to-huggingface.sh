#!/bin/bash

# SafeGuard AI - Manual Hugging Face Deployment Script
# Deploy backend to Hugging Face Spaces

set -e

echo "🤗 SafeGuard AI - Hugging Face Deployment"
echo "========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ git is not installed"
    exit 1
fi

# Get Hugging Face credentials
echo "Enter your Hugging Face username:"
read -r HF_USERNAME

echo "Enter your Hugging Face Space name (e.g., safeguard-ai-backend):"
read -r HF_SPACE_NAME

echo "Enter your Hugging Face API token:"
read -rs HF_TOKEN
echo ""

HF_SPACE_URL="https://huggingface.co/spaces/$HF_USERNAME/$HF_SPACE_NAME"
echo "📦 Target Space: $HF_SPACE_URL"
echo ""

# Check if Space exists
echo "🔍 Checking if Space exists..."
if git ls-remote "https://huggingface.co/spaces/$HF_USERNAME/$HF_SPACE_NAME" &> /dev/null; then
    echo "✅ Space exists, will update it"
    UPDATE_MODE=true
else
    echo "⚠️  Space does not exist"
    echo "Please create it first at: https://huggingface.co/new-space"
    echo "  - Name: $HF_SPACE_NAME"
    echo "  - License: MIT"
    echo "  - SDK: Docker"
    echo "  - Hardware: CPU Basic (or higher for production)"
    echo ""
    echo "After creating the Space, run this script again."
    exit 1
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "📁 Using temp directory: $TEMP_DIR"

# Clone the Hugging Face Space
echo "📥 Cloning Hugging Face Space..."
git clone "https://$HF_USERNAME:$HF_TOKEN@huggingface.co/spaces/$HF_USERNAME/$HF_SPACE_NAME" "$TEMP_DIR"

# Copy backend files
echo "📋 Copying backend files..."
cp -r backend/* "$TEMP_DIR/"
cp backend/Dockerfile "$TEMP_DIR/Dockerfile"

# Create README.md for Space
cat > "$TEMP_DIR/README.md" << 'EOF'
---
title: SafeGuard AI Backend
emoji: 🛡️
colorFrom: blue
colorTo: cyan
sdk: docker
pinned: false
---

# SafeGuard AI - Threat Detection Backend

Real-time humanitarian threat detection API powered by YOLOv8, MediaPipe, and OpenAI.

## Features

- 🎯 YOLOv8 object detection for weapons, dangerous items
- 👤 Human activity recognition (falling, sleeping, eyes closed)
- 🤖 AI-powered threat analysis with GPT-4
- 📧 Multi-channel alerts (Email, SMS, Call)
- 🌊 WebSocket support for real-time detection
- 📊 RESTful API with FastAPI

## API Endpoints

- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `WebSocket /ws/detect/{user_id}` - Real-time detection stream
- `POST /api/chat` - AI analyst chat
- `GET /api/threat-assessment` - Quick threat assessment

## Environment Variables

Configure these in your Space settings:

- `OPENAI_API_KEY` - OpenAI API key for GPT-4
- `EMAIL_FROM` - Alert email sender
- `EMAIL_PASSWORD` - Gmail app password
- `EMAIL_TO` - Alert recipient email
- `OPENWEATHER_API_KEY` - Weather API key (optional)

## Usage

```python
import websockets
import asyncio
import json
import base64

async def detect():
    uri = "wss://your-space.hf.space/ws/detect/user123"
    async with websockets.connect(uri) as ws:
        # Send frame
        with open("frame.jpg", "rb") as f:
            frame_b64 = base64.b64encode(f.read()).decode()

        await ws.send(json.dumps({
            "type": "frame",
            "frame": f"data:image/jpeg;base64,{frame_b64}"
        }))

        # Receive detection
        result = await ws.recv()
        print(json.loads(result))

asyncio.run(detect())
```

## License

MIT License

## Author

SafeGuard AI Team
EOF

# Configure environment variables prompt
echo ""
echo "⚙️  IMPORTANT: Configure Environment Variables"
echo "Go to your Space settings and add the following secrets:"
echo "  1. OPENAI_API_KEY - Your OpenAI API key"
echo "  2. EMAIL_FROM - Sender email (e.g., your@gmail.com)"
echo "  3. EMAIL_PASSWORD - Gmail app password"
echo "  4. EMAIL_TO - Recipient email"
echo "  5. SMTP_HOST - smtp.gmail.com"
echo "  6. SMTP_PORT - 587"
echo "  7. OPENWEATHER_API_KEY - (optional) Weather API key"
echo ""
echo "Settings URL: $HF_SPACE_URL/settings"
echo ""
read -p "Press Enter after configuring environment variables..."

# Commit and push
cd "$TEMP_DIR"
git add .
git commit -m "Deploy SafeGuard AI Backend from local" || echo "No changes to commit"

echo "🚀 Pushing to Hugging Face Space..."
git push origin main

# Cleanup
cd - > /dev/null
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Your Space:"
echo "  URL: $HF_SPACE_URL"
echo "  API: https://$HF_USERNAME-$HF_SPACE_NAME.hf.space"
echo "  Docs: https://$HF_USERNAME-$HF_SPACE_NAME.hf.space/docs"
echo "  Health: https://$HF_USERNAME-$HF_SPACE_NAME.hf.space/health"
echo ""
echo "⏳ Space is building... Monitor at: $HF_SPACE_URL"
echo "   Building usually takes 5-10 minutes for first deployment"
echo ""
echo "🔧 Next steps:"
echo "  1. Wait for Space to finish building"
echo "  2. Test health endpoint"
echo "  3. Update frontend NEXT_PUBLIC_API_URL to point to your Space"
echo "  4. Deploy frontend to Vercel"

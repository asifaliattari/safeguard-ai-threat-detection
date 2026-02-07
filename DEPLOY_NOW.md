# 🚀 DEPLOY NOW - Step-by-Step Guide

**Follow these exact steps to deploy SafeGuard AI to production**

## ✅ Step 1: Get Your API Keys (5 minutes)

### 1.1 OpenAI API Key
1. Go to: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Name: "SafeGuard AI Production"
4. Copy the key (starts with `sk-proj-...`)
5. **Save it somewhere safe!**

### 1.2 Gmail App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Name: "SafeGuard AI"
4. Copy the 16-character password
5. **Save it somewhere safe!**

### 1.3 Hugging Face Token
1. Go to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: "SafeGuard AI Deploy"
4. Type: **Write** ⚠️ (Important - must be "Write" not "Read")
5. Click "Generate token"
6. Copy the token (starts with `hf_...`)
7. **Save it somewhere safe!**

### 1.4 Vercel Token
1. Go to: https://vercel.com/account/tokens
2. Click "Create"
3. Name: "SafeGuard AI"
4. Copy the token
5. **Save it somewhere safe!**

---

## ✅ Step 2: Create Hugging Face Space (2 minutes)

1. **Go to**: https://huggingface.co/new-space

2. **Fill in the form**:
   ```
   Owner: [Your HF username]
   Space name: safeguard-ai-backend
   License: MIT
   Space SDK: Docker ⚠️ (MUST select Docker!)
   Space hardware: CPU Basic (Free) or CPU Upgrade ($0.03/hour - faster)
   Visibility: Public
   ```

3. **Click "Create Space"**

4. **Your Space URL will be**:
   ```
   https://huggingface.co/spaces/[YOUR_USERNAME]/safeguard-ai-backend
   ```

5. **Go to Settings** → **Variables and secrets**

6. **Add these secrets** (click "New secret" for each):

   | Name | Value |
   |------|-------|
   | `OPENAI_API_KEY` | Your OpenAI key from Step 1.1 |
   | `EMAIL_FROM` | asif.alimusharaf@gmail.com |
   | `EMAIL_PASSWORD` | Your Gmail app password from Step 1.2 |
   | `EMAIL_TO` | asif.alimusharaf@gmail.com |
   | `SMTP_HOST` | smtp.gmail.com |
   | `SMTP_PORT` | 587 |

7. **Save all secrets**

---

## ✅ Step 3: Deploy Backend to Hugging Face (3 minutes)

**Open PowerShell or Command Prompt** and run:

```powershell
cd "C:\Users\Fattani Computers\projectmit"
```

**Then run this interactive deployment**:

```powershell
# I'll guide you through this - just follow the prompts
git clone https://huggingface.co/spaces/[YOUR_HF_USERNAME]/safeguard-ai-backend hf-deploy-temp
```

**Replace `[YOUR_HF_USERNAME]` with your actual Hugging Face username!**

Example: If your username is `asifali`:
```powershell
git clone https://huggingface.co/spaces/asifali/safeguard-ai-backend hf-deploy-temp
```

**Enter your Hugging Face token when prompted for password**

Then continue:

```powershell
# Copy backend files
xcopy /E /I backend\* hf-deploy-temp\
copy backend\Dockerfile hf-deploy-temp\Dockerfile

# Create README for Hugging Face
cd hf-deploy-temp
```

Now create the README.md file (I'll create this for you below).

---

## ✅ Step 4: Create Hugging Face Space README

**Run this command**:

```powershell
# This will create the README - copy and paste this entire block:

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
echo - 🎯 YOLOv8 object detection for weapons, dangerous items
echo - 👤 Human activity recognition (falling, sleeping, eyes closed)
echo - 🤖 AI-powered threat analysis with GPT-4
echo - 📧 Multi-channel alerts (Email, SMS, Call)
echo - 🌊 WebSocket support for real-time detection
echo - 📊 RESTful API with FastAPI
echo.
echo ## API Endpoints
echo.
echo - `GET /health` - Health check
echo - `GET /docs` - Interactive API documentation
echo - `WebSocket /ws/detect/{user_id}` - Real-time detection stream
echo.
echo ## Authors
echo.
echo - **Asif Ali** - Lead Developer ^& AI Engineer
echo - **Sharmeen Asif** - Co-Developer ^& System Architect
echo.
echo GitHub: https://github.com/asifaliattari/safeguard-ai-threat-detection
echo.
echo ## License
echo.
echo MIT License - Copyright (c) 2025 Asif Ali ^& Sharmeen Asif
) > README.md
```

---

## ✅ Step 5: Push to Hugging Face (1 minute)

```powershell
git add .
git commit -m "Initial deployment of SafeGuard AI Backend by Asif Ali & Sharmeen Asif"
git push origin main
```

**Enter your Hugging Face token when prompted for password**

---

## ✅ Step 6: Wait for Build (5-10 minutes)

1. **Go to your Space**: https://huggingface.co/spaces/[YOUR_USERNAME]/safeguard-ai-backend
2. **Click "Logs" tab** to watch it build
3. Wait for "Running" status (green)

**Your backend URL will be**:
```
https://[YOUR_USERNAME]-safeguard-ai-backend.hf.space
```

**Test it**:
```powershell
curl https://[YOUR_USERNAME]-safeguard-ai-backend.hf.space/health
```

Expected response:
```json
{"status":"healthy","service":"SafeGuard AI Enhanced","version":"2.0.0"}
```

---

## ✅ Step 7: Deploy Frontend to Vercel (2 minutes)

**Clean up and go to frontend**:

```powershell
cd ..
rmdir /S /Q hf-deploy-temp
cd frontend
```

**Login to Vercel**:

```powershell
vercel login
```

Follow the browser prompts to login.

**Deploy to Vercel**:

```powershell
vercel --prod
```

**When prompted**:
- Set up and deploy: **Y**
- Which scope: Select your account
- Link to existing project: **N**
- Project name: **safeguard-ai-frontend**
- Directory: `.` (just press Enter)
- Override settings: **N**

**Set environment variables** (you'll be prompted):

When asked, add:
```
NEXT_PUBLIC_API_URL=https://[YOUR_HF_USERNAME]-safeguard-ai-backend.hf.space
NEXT_PUBLIC_WS_URL=wss://[YOUR_HF_USERNAME]-safeguard-ai-backend.hf.space
```

**Replace `[YOUR_HF_USERNAME]` with your actual username!**

---

## ✅ Step 8: Test Production System (2 minutes)

1. **Open your Vercel URL** (shown after deployment)
   - Example: `https://safeguard-ai-frontend.vercel.app`

2. **Click "Start AI Detection"**

3. **Allow camera access**

4. **Test features**:
   - ✅ Video feed shows
   - ✅ Detection boxes appear
   - ✅ Audio alerts play when threats detected
   - ✅ AI chatbot responds

---

## 🎉 SUCCESS!

Your SafeGuard AI is now live in production!

**Your URLs**:
- **Frontend**: https://safeguard-ai-frontend-[random].vercel.app
- **Backend**: https://[YOUR_USERNAME]-safeguard-ai-backend.hf.space
- **API Docs**: https://[YOUR_USERNAME]-safeguard-ai-backend.hf.space/docs

---

## 📊 Share Your Project

Update your GitHub README with production URLs:

```markdown
## 🌐 Live Demo

- **Frontend**: https://your-frontend-url.vercel.app
- **Backend API**: https://your-backend-url.hf.space
- **API Documentation**: https://your-backend-url.hf.space/docs
```

---

## ❓ Need Help?

If you get stuck, check:
1. Hugging Face Space logs
2. Vercel deployment logs
3. DEPLOYMENT_GUIDE.md for detailed troubleshooting

**Common Issues**:

- **Space won't build**: Check you selected "Docker" SDK
- **Environment variables missing**: Go to Space Settings → Variables
- **Frontend can't connect**: Check NEXT_PUBLIC_API_URL is correct
- **WebSocket fails**: Check NEXT_PUBLIC_WS_URL uses `wss://` not `ws://`

---

**Developed by Asif Ali & Sharmeen Asif** 🛡️

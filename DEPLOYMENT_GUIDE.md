# SafeGuard AI - Deployment Guide

Complete guide for deploying SafeGuard AI to production (Hugging Face + Vercel).

## 🎯 Overview

- **Backend**: Hugging Face Spaces (Docker SDK)
- **Frontend**: Vercel (Next.js)
- **CI/CD**: GitHub Actions
- **Models**: Git LFS (88MB)

## 📋 Prerequisites

- [x] GitHub account
- [x] Hugging Face account ([sign up](https://huggingface.co/join))
- [x] Vercel account ([sign up](https://vercel.com/signup))
- [x] Git LFS installed
- [x] Node.js 20+ installed
- [x] Python 3.11+ installed

## 🔐 Step 1: Rotate API Keys

Before deploying, create NEW API keys (never reuse exposed keys):

### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Name it "SafeGuard AI Production"
4. Copy the key (starts with `sk-proj-...`)

### Gmail App Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Name it "SafeGuard AI"
4. Copy the 16-character password

### Hugging Face Token
1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: "SafeGuard AI Deploy"
4. Type: **Write** (required for pushing to Spaces)
5. Copy the token

### Vercel Token
1. Go to https://vercel.com/account/tokens
2. Click "Create"
3. Name: "SafeGuard AI CI/CD"
4. Copy the token

## 🚀 Step 2: Create Hugging Face Space

1. Go to https://huggingface.co/new-space
2. Configure:
   - **Owner**: Your username
   - **Space name**: `safeguard-ai-backend`
   - **License**: MIT
   - **Select the Space SDK**: Docker
   - **Space hardware**: CPU Basic (free) or CPU Upgrade (faster)
   - **Visibility**: Public
3. Click "Create Space"
4. **Important**: Go to Settings → Variables and add:
   ```
   OPENAI_API_KEY=your-new-openai-key
   EMAIL_FROM=your-email@gmail.com
   EMAIL_PASSWORD=your-gmail-app-password
   EMAIL_TO=recipient@example.com
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   OPENWEATHER_API_KEY=your-weather-key (optional)
   ```

## 🔧 Step 3: Configure GitHub Secrets

Run the automated setup script:

```bash
cd projectmit
bash scripts/setup-github-secrets.sh
```

Or manually add secrets at `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`:

| Secret Name | Value |
|-------------|-------|
| `HF_TOKEN` | Your Hugging Face write token |
| `HF_USERNAME` | Your Hugging Face username |
| `HF_SPACE_NAME` | `safeguard-ai-backend` |
| `VERCEL_TOKEN` | Your Vercel token |
| `OPENAI_API_KEY` | Your NEW OpenAI key |
| `EMAIL_FROM` | Your Gmail address |
| `EMAIL_PASSWORD` | Your Gmail app password |
| `EMAIL_TO` | Alert recipient email |
| `NEXT_PUBLIC_API_URL` | `https://YOUR_HF_USERNAME-safeguard-ai-backend.hf.space` |
| `NEXT_PUBLIC_WS_URL` | `wss://YOUR_HF_USERNAME-safeguard-ai-backend.hf.space` |

## 📦 Step 4: Push to GitHub

```bash
# Create GitHub repository
gh repo create safeguard-ai-threat-detection --public --source=. --remote=origin

# Push code (Git LFS will upload models automatically)
git push -u origin master

# Verify LFS files
git lfs ls-files
```

Expected output:
```
f59b3d833e * backend/yolov8n.pt
64184e229b * face_landmarker.task
6c25b0b63b * models/yolov8m.pt
268e5bb54c * models/yolov8s.pt
c6fa93dd1e * yolov8n-pose.pt
```

## 🤗 Step 5: Deploy Backend to Hugging Face

### Option A: Automated (via GitHub Actions)

Push triggers automatic deployment:

```bash
git add .
git commit -m "feat: Trigger production deployment"
git push origin master
```

Monitor at: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`

### Option B: Manual

```bash
bash scripts/deploy-to-huggingface.sh
```

**Verify Deployment:**

```bash
# Check health
curl https://YOUR_HF_USERNAME-safeguard-ai-backend.hf.space/health

# Expected response:
{
  "status": "healthy",
  "service": "SafeGuard AI Enhanced",
  "version": "2.0.0"
}
```

**View API Docs:**
`https://YOUR_HF_USERNAME-safeguard-ai-backend.hf.space/docs`

## ▲ Step 6: Deploy Frontend to Vercel

### Option A: Automated (via GitHub Actions)

Already set up! Push to master triggers deployment.

### Option B: Manual

```bash
cd frontend
bash ../scripts/deploy-to-vercel.sh
```

**Verify Deployment:**

Visit your Vercel URL and:
1. Click "Start AI Detection"
2. Allow camera permissions
3. Test detection with objects
4. Test audio alerts
5. Test AI chatbot

## 🔄 Step 7: Test CI/CD Pipeline

```bash
# Trigger empty commit to test pipeline
git commit --allow-empty -m "test: Verify CI/CD pipeline"
git push origin master
```

**Monitor:**
- GitHub Actions: Check workflows succeed
- Hugging Face: Space rebuilds and deploys
- Vercel: Frontend redeploys

## 🧪 Step 8: Run Load Tests

### Test Local Stack

```bash
# Start local services
docker-compose up -d

# Wait for services
sleep 30

# Run load test
python scripts/load-test.py ws://localhost:8000 --users 10 --frames 100
```

### Test Production

```bash
# Test Hugging Face backend
python scripts/load-test.py wss://YOUR_HF_USERNAME-safeguard-ai-backend.hf.space --users 5 --frames 50
```

**Expected Results:**
- Success rate: >95%
- Average latency: <1000ms
- Throughput: >5 FPS

## 📊 Production URLs

After deployment, your URLs will be:

- **Frontend**: `https://safeguard-ai-frontend-YOUR_VERCEL.vercel.app`
- **Backend API**: `https://YOUR_HF_USERNAME-safeguard-ai-backend.hf.space`
- **API Docs**: `https://YOUR_HF_USERNAME-safeguard-ai-backend.hf.space/docs`
- **Health Check**: `https://YOUR_HF_USERNAME-safeguard-ai-backend.hf.space/health`

## 🔍 Monitoring

### Hugging Face Spaces

- **Logs**: Click "Logs" tab in your Space
- **Metrics**: Check CPU/RAM usage
- **Settings**: Manage environment variables

### Vercel

- **Dashboard**: https://vercel.com/dashboard
- **Deployments**: View deployment history
- **Analytics**: Monitor traffic and performance

### GitHub Actions

- **Workflows**: Monitor CI/CD runs
- **Logs**: Debug failed deployments

## 🐛 Troubleshooting

### Backend Issues

**Space won't build:**
```bash
# Check logs in Hugging Face Space
# Common issues:
- Missing environment variables
- Git LFS files not pulled
- Insufficient hardware
```

**Health check fails:**
```bash
# SSH into Space (if enabled)
# Check container logs
docker logs <container_id>
```

### Frontend Issues

**Build fails on Vercel:**
- Check environment variables are set
- Verify NEXT_PUBLIC_API_URL is correct
- Check Vercel build logs

**WebSocket connection fails:**
- Verify NEXT_PUBLIC_WS_URL uses `wss://` not `ws://`
- Check CORS settings in backend

### CI/CD Issues

**GitHub Actions fails:**
```bash
# Check secrets are configured
gh secret list

# View workflow logs
gh run view --log
```

## 🔒 Security Checklist

- [x] `.env` not in git history
- [x] All API keys rotated
- [x] GitHub secrets configured
- [x] Hugging Face environment variables set
- [x] `.env.example` created
- [x] `.gitignore` includes `.env`

## 📚 Additional Resources

- [Hugging Face Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [Vercel Deployment Docs](https://vercel.com/docs)
- [Git LFS Tutorial](https://git-lfs.github.com/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

## 🆘 Support

If you encounter issues:

1. Check logs (Hugging Face, Vercel, GitHub Actions)
2. Verify environment variables
3. Test local stack first: `bash scripts/test-local.sh`
4. Open issue on GitHub

## 🎉 Success!

Your SafeGuard AI system is now deployed and ready for production use!

**Next Steps:**
1. Share frontend URL with stakeholders
2. Set up monitoring alerts
3. Configure autoscaling if needed
4. Document API usage for integration
5. Plan feature enhancements

---

**Deployment Time Estimate:**
- Setup: 1 hour
- Deployment: 30 minutes
- Testing: 30 minutes
- **Total: ~2 hours**

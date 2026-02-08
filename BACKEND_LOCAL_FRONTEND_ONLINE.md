# 🌐 Backend Local + Frontend Online Setup

**By Asif Ali & Sharmeen Asif**

Run backend on your computer, use frontend online from Vercel!

---

## 🎯 What This Does

- ✅ **Backend**: Runs on your computer (localhost:8000)
- ✅ **ngrok**: Exposes your local backend to internet
- ✅ **Frontend**: Uses your deployed Vercel site
- ✅ **Result**: Access from anywhere, backend on your PC!

---

## 📋 Quick Setup (3 Steps)

### **Step 1: Install ngrok** (One-time, 2 minutes)

1. **Download ngrok**:
   - Go to: https://ngrok.com/download
   - Click "Windows (64-bit)" → Download ZIP
   - Extract `ngrok.exe` to `C:\Windows\System32`

2. **Sign up for free**:
   - Go to: https://dashboard.ngrok.com/signup
   - Sign up with email or GitHub
   - It's 100% FREE!

3. **Get your authtoken**:
   - After signup, go to: https://dashboard.ngrok.com/get-started/your-authtoken
   - Copy your authtoken

4. **Configure ngrok**:
   ```bash
   ngrok config add-authtoken YOUR_TOKEN_HERE
   ```
   (Replace YOUR_TOKEN_HERE with your actual token)

✅ Done! ngrok is ready!

---

### **Step 2: Start Backend + ngrok** (30 seconds)

**Double-click this file:**
```
START_BACKEND_ONLINE.bat
```

This will:
1. Start backend with Docker
2. Open ngrok tunnel
3. Give you a public URL

**You'll see a new window with ngrok running!**

**KEEP THE NGROK WINDOW OPEN!**

---

### **Step 3: Copy ngrok URL** (10 seconds)

In the ngrok window, look for:

```
Forwarding    https://abc123.ngrok-free.app -> http://localhost:8000
```

**Copy the HTTPS URL**: `https://abc123.ngrok-free.app`

---

### **Step 4: Update Vercel** (1 minute)

Open **PowerShell or Command Prompt**:

```bash
cd "C:\Users\Fattani Computers\projectmit\frontend"
```

**Set API URL:**
```bash
vercel env rm NEXT_PUBLIC_API_URL production
vercel env add NEXT_PUBLIC_API_URL production
```
When prompted, paste: `https://YOUR-NGROK-URL.ngrok-free.app`

**Set WebSocket URL:**
```bash
vercel env rm NEXT_PUBLIC_WS_URL production
vercel env add NEXT_PUBLIC_WS_URL production
```
When prompted, paste: `wss://YOUR-NGROK-URL.ngrok-free.app`

(Replace `https` with `wss` for WebSocket!)

**Redeploy frontend:**
```bash
vercel --prod
```

✅ **DONE!** Wait 30 seconds for deployment.

---

## 🎉 IT'S WORKING!

**Open your Vercel frontend:**
https://frontend-beige-kappa-38.vercel.app

**Check top-right corner:**
- Status button should be **🟢 GREEN "✓ Backend Online"**

**Start Detection:**
1. Click "Start AI Detection"
2. Allow camera
3. **Works from ANYWHERE!**

Your friends can use your frontend URL and it will connect to YOUR local backend! 🚀

---

## 🔄 Every Time You Want to Use

1. **Start backend + ngrok:**
   ```
   Double-click: START_BACKEND_ONLINE.bat
   ```

2. **Copy new ngrok URL** (changes each time on free plan)

3. **Update Vercel** (run the commands from Step 4 above)

**That's it!** Takes 2 minutes total.

---

## 💡 Pro Tips

### Keep ngrok URL Same (Upgrade to Paid)

Free ngrok = URL changes every time
Paid ngrok ($8/month) = Fixed URL (no need to update Vercel!)

**Or use ngrok domains (free):**
```bash
ngrok http 8000 --domain=your-custom-name.ngrok-free.app
```

### Auto-Update Vercel (Advanced)

Create `update-vercel.bat`:
```batch
@echo off
set NGROK_URL=%1
cd frontend
echo %NGROK_URL% | vercel env add NEXT_PUBLIC_API_URL production --force
echo wss://%NGROK_URL:~8% | vercel env add NEXT_PUBLIC_WS_URL production --force
vercel --prod
```

Use:
```bash
update-vercel.bat abc123.ngrok-free.app
```

---

## 📊 Your Setup

```
┌─────────────────────────────────────────┐
│  Users (Anywhere in the World)          │
│  👥👥👥                                   │
└─────────────┬───────────────────────────┘
              │
              │ HTTPS
              ▼
┌─────────────────────────────────────────┐
│  Vercel Frontend (Online)               │
│  https://frontend-beige-kappa-38...     │
│  🌐 Next.js Web App                     │
└─────────────┬───────────────────────────┘
              │
              │ HTTPS/WSS
              ▼
┌─────────────────────────────────────────┐
│  ngrok Tunnel (Online)                  │
│  https://abc123.ngrok-free.app          │
│  🌉 Public Gateway                      │
└─────────────┬───────────────────────────┘
              │
              │ HTTP
              ▼
┌─────────────────────────────────────────┐
│  Your Computer (Local)                  │
│  http://localhost:8000                  │
│  🖥️  FastAPI Backend + AI Models        │
│  🐳 Docker Container                     │
└─────────────────────────────────────────┘
```

---

## ✅ Checklist

Before starting:
- [ ] Docker Desktop installed and running
- [ ] ngrok installed and configured
- [ ] Vercel CLI logged in

To run:
- [ ] Double-click `START_BACKEND_ONLINE.bat`
- [ ] ngrok window opens and shows URL
- [ ] Copy ngrok HTTPS URL
- [ ] Update Vercel environment variables
- [ ] Redeploy Vercel frontend
- [ ] Open Vercel URL
- [ ] Backend status shows GREEN ✓

---

## 🆘 Troubleshooting

### ngrok Window Closes Immediately

- Check if port 8000 is already in use
- Wait for backend to fully start (30 seconds)
- Try manually: `ngrok http 8000`

### Vercel Shows "Backend Offline" (Red)

- Check ngrok URL is correct (HTTPS not HTTP)
- Check ngrok window is still open
- Test ngrok URL: `https://YOUR-URL.ngrok-free.app/health`
- Wait 1-2 minutes for Vercel to redeploy

### ngrok Says "Failed to Start Tunnel"

- Your authtoken might be wrong
- Run: `ngrok config add-authtoken YOUR_TOKEN`
- Get token from: https://dashboard.ngrok.com/get-started/your-authtoken

### Backend Won't Start

- Check Docker Desktop is running
- Run: `docker-compose logs backend`
- Try: `docker-compose restart backend`

---

## 🎯 Quick Commands Reference

**Start backend:**
```bash
START_BACKEND_ONLINE.bat
```

**Test backend locally:**
```bash
curl http://localhost:8000/health
```

**Test ngrok URL:**
```bash
curl https://YOUR-NGROK-URL.ngrok-free.app/health
```

**Update Vercel:**
```bash
cd frontend
vercel env add NEXT_PUBLIC_API_URL production
vercel env add NEXT_PUBLIC_WS_URL production
vercel --prod
```

**View logs:**
```bash
docker-compose logs -f backend
```

**Stop backend:**
```bash
docker-compose down
```

---

## 🎉 Benefits

✅ **Backend Power**: Your local GPU, CPU, models
✅ **Frontend Anywhere**: Access from any device
✅ **Easy Sharing**: Share Vercel URL with others
✅ **Full Control**: Backend runs on your computer
✅ **Cost**: 100% FREE (ngrok + Vercel free tiers)

---

## 🚀 Ready!

1. Install ngrok (one-time)
2. Run `START_BACKEND_ONLINE.bat`
3. Update Vercel
4. Use your app from anywhere!

---

**Developed by Asif Ali & Sharmeen Asif** 🛡️

**GitHub**: https://github.com/asifaliattari/safeguard-ai-threat-detection
**Frontend**: https://frontend-beige-kappa-38.vercel.app

# 🚀 SafeGuard AI - Local Setup Guide

**By Asif Ali & Sharmeen Asif**

Run the complete SafeGuard AI system on your computer in 2 minutes!

---

## ✅ Prerequisites

You only need **Docker Desktop** installed:

**Download**: https://www.docker.com/products/docker-desktop

- Windows 10/11: Download and install
- Start Docker Desktop
- Wait for it to say "Docker is running"

---

## 🎯 Super Easy Start (1-Click!)

**Just double-click this file:**

```
START_SAFEGUARD_LOCAL.bat
```

That's it! Everything will start automatically! 🎉

---

## 📊 What Starts Automatically

✅ **Backend API** - http://localhost:8000
✅ **Frontend Web App** - http://localhost:3000
✅ **PostgreSQL Database** - Automatic
✅ **Redis Cache** - Automatic

---

## 🌐 Access Your App

After starting (wait 30 seconds for first-time setup):

1. **Frontend opens automatically** in your browser
2. Or manually go to: **http://localhost:3000**
3. **Look at the top-right corner** → Backend status button
4. Should show: **"✓ Backend Online"** in GREEN 🟢

---

## 🎥 Using SafeGuard AI

1. Click **"Start AI Detection"** button
2. Allow camera access
3. Backend status = **GREEN** ✓
4. Point camera at objects
5. Watch real-time threat detection!
6. Audio alerts play automatically

---

## 🛑 How to Stop

**Option 1: Easy way**
- Close the command window showing logs
- Run in new command prompt:
  ```bash
  docker-compose down
  ```

**Option 2: From command prompt**
```bash
cd "C:\Users\Fattani Computers\projectmit"
docker-compose down
```

---

## 📋 Useful Commands

### View Logs
```bash
docker-compose logs -f
```

### View Backend Logs Only
```bash
docker-compose logs -f backend
```

### View Frontend Logs Only
```bash
docker-compose logs -f frontend
```

### Restart Everything
```bash
docker-compose restart
```

### Rebuild After Code Changes
```bash
docker-compose up --build
```

### Check Status
```bash
docker-compose ps
```

---

## 🔧 Troubleshooting

### Backend Status Shows RED ❌

**Wait 30-60 seconds** - First startup takes time to:
- Download Docker images
- Install Python packages
- Download AI models
- Start all services

**Check logs:**
```bash
docker-compose logs backend
```

### Camera Not Working

- **Allow camera permissions** in browser
- **Use Chrome or Edge** (best compatibility)
- Check if another app is using camera

### Port Already in Use

If you get "port already in use" error:

**Stop other apps using these ports:**
- Port 3000 (Frontend)
- Port 8000 (Backend)
- Port 5432 (PostgreSQL)
- Port 6379 (Redis)

Or change ports in `docker-compose.yml`

### Docker Not Running

1. Open **Docker Desktop**
2. Wait for it to start completely
3. Try again

---

## 🎯 What the Status Button Shows

| Color | Status | Meaning |
|-------|--------|---------|
| 🟢 GREEN | ✓ Backend Online | Everything working! |
| 🔴 RED | ✗ Backend Offline | Backend not running |
| 🟡 YELLOW | ⏳ Checking... | Connecting... |

**Click the status button** to manually refresh!

The button **auto-checks every 10 seconds** automatically.

---

## 📦 What's Running

Open **Docker Desktop** → **Containers** to see:

- `projectmit-backend-1` - FastAPI + AI models
- `projectmit-frontend-1` - Next.js web app
- `projectmit-postgres-1` - PostgreSQL database
- `projectmit-redis-1` - Redis cache

All are connected in a Docker network automatically!

---

## 🌐 Your URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Main web interface |
| **Backend API** | http://localhost:8000 | API server |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | Backend health status |

---

## 💡 Pro Tips

1. **Keep Docker Desktop running** while using the app
2. **First startup is slow** (~2-3 minutes) - be patient!
3. **Subsequent starts are fast** (~10 seconds)
4. **Watch the status button** - wait for green before starting detection
5. **Test audio alerts** - turn volume up!

---

## ✅ Success Checklist

- [ ] Docker Desktop installed and running
- [ ] Ran `START_SAFEGUARD_LOCAL.bat`
- [ ] Frontend opened at http://localhost:3000
- [ ] Backend status shows **GREEN** ✓
- [ ] Clicked "Start AI Detection"
- [ ] Camera permission allowed
- [ ] Detection boxes appear on video
- [ ] Audio alerts working

---

## 🆘 Need Help?

1. **Check logs**: `docker-compose logs -f`
2. **Restart services**: `docker-compose restart`
3. **Full reset**: `docker-compose down` then `START_SAFEGUARD_LOCAL.bat`
4. **Check Docker Desktop** is running

---

## 🎉 You're Ready!

Just run:
```
START_SAFEGUARD_LOCAL.bat
```

And access:
```
http://localhost:3000
```

**Enjoy your AI-powered threat detection system!** 🛡️

---

**Developed by Asif Ali & Sharmeen Asif**

**GitHub**: https://github.com/asifaliattari/safeguard-ai-threat-detection

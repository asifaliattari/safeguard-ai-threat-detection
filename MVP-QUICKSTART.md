# 🚀 MVP Quick Start Guide

**Get SafeGuard AI running in 10 minutes!**

## ✅ What's Ready

- ✅ Next.js frontend with live video feed
- ✅ FastAPI backend with YOLOv8 detection
- ✅ WebSocket real-time streaming
- ✅ Bounding box overlay
- ✅ Danger alerts for weapons

## 🏃 Quick Start (3 Steps)

### Step 1: Install Backend Dependencies (2 min)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# Install dependencies (this will take ~2 minutes)
pip install fastapi uvicorn websockets opencv-python-headless ultralytics numpy python-dotenv slowapi
```

### Step 2: Start Backend (1 min)

```bash
# Make sure you're in backend/ and venv is activated
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
🚀 SafeGuard AI Backend Starting...
📡 WebSocket endpoint: ws://localhost:8000/ws/detect/{user_id}
📚 API Docs: http://localhost:8000/api/docs
⚠️  YOLOv8 will download on first detection (~6MB)
```

**Keep this terminal open!**

### Step 3: Start Frontend (1 min)

Open a **NEW terminal**:

```bash
cd frontend
npm run dev
```

You should see:
```
✓ Ready in 2.5s
○ Local:   http://localhost:3000
```

## 🎬 Demo Time!

1. Open **http://localhost:3000** in Chrome/Edge (Safari may have issues)

2. Click **"Start AI Detection"**

3. Allow camera access

4. Point camera at:
   - ✅ **People** → Blue boxes appear
   - ✅ **Objects** → Blue boxes appear
   - ⚠️ **Scissors/Knife** → RED boxes + DANGER alert!

5. Watch the detection log fill up on the right!

## 📊 What You'll See

### Frontend (http://localhost:3000)
- Live camera feed
- Real-time bounding boxes
- Detection stats (Total / Weapons / People)
- Recent detection log
- RED danger alerts for weapons

### Backend Terminal
```
✅ User demo-user connected
🎯 Detected 3 objects for demo-user
📊 Processed 30 frames for demo-user
```

## 🐛 Troubleshooting

### Camera not working?
- **Allow camera permissions** in browser
- Use **Chrome or Edge** (better WebRTC support)
- Check if another app is using camera

### Backend won't start?
```bash
# Make sure you activated venv
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install missing packages
pip install fastapi uvicorn ultralytics opencv-python-headless
```

### WebSocket connection failed?
- Make sure backend is running on port 8000
- Check http://localhost:8000/health
- CORS is wide open for MVP (no restrictions)

### YOLOv8 download stuck?
- First detection will download ~6MB model
- Wait 30 seconds, it will complete
- Model downloads to `~/.ultralytics/`

### No detections appearing?
- Point camera at **clear, well-lit objects**
- Try a **water bottle, phone, or scissors**
- Confidence threshold is 40% (pretty sensitive)

## 🎯 Demo Tips

**Best objects to demo:**
1. **Person** - Step into frame
2. **Cell phone** - Hold up your phone
3. **Scissors** - DANGER alert will trigger!
4. **Cup/Bottle** - Easy to detect
5. **Chair/Laptop** - Any common object

**For impressive demo:**
1. Start with normal objects (phone, cup)
2. Show detection log filling up
3. **Then show scissors** → Watch RED alert appear!
4. Point out the stats counter updating

## 📱 What's NOT in MVP

These features are for future phases:
- ❌ Database (all in-memory for now)
- ❌ User authentication
- ❌ LLM diagnosis (Claude integration)
- ❌ Email alerts
- ❌ Multiple cameras
- ❌ Recording/history

## ⏱️ Performance

**Expected:**
- Frontend: 10 FPS (frames sent to backend)
- Backend: 5-8 FPS (detection speed on CPU)
- Latency: < 200ms end-to-end

**If slow:**
- Lower video resolution (edit frontend/app/page.tsx line 33)
- Reduce FPS (edit line 118, change 100 to 200)
- Backend will use CPU (GPU support in future)

## 🚀 You're Ready for Demo!

**Demo Script (2 minutes):**

1. "This is SafeGuard AI - real-time video threat detection"
2. Click Start → Camera opens
3. "Using YOLOv8 AI model to detect objects in real-time"
4. Show normal objects → detections appear
5. "Now watch what happens with dangerous objects"
6. Show scissors → RED DANGER alert!
7. "System can detect weapons, people, vehicles, and hazards"
8. Point to detection log: "All logged in real-time"
9. Point to stats: "Tracking total detections and threats"

**That's it! You have a working AI detection system!** 🎉

---

## 📝 Next Steps After Demo

If your demo goes well, we can add:
- LLM-powered threat analysis (Claude)
- Email/SMS alerts
- Database storage
- Multi-camera support
- Historical analysis
- Custom detection rules

Let me know what features are most important!

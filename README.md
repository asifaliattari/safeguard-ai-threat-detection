# 🚨 SafeGuard AI - Live Threat Detection System

**Real-time AI threat detection with audio alerts**

## 👥 Development Team

**Created by:**
- **Asif Ali** - Lead Developer & AI Engineer
- **Sharmeen Asif** - Co-Developer & System Architect

---

## ✨ Features

- 😴 **Sleeping/Eyes Closed** detection
- 🤕 **Person Falling** detection
- 💀 **Unconscious People** detection
- 🏊 **Drowning** detection
- 🔪 **Weapons** (guns, knives, dangerous objects)
- 🔊 **Audio Beep Alarm** on every threat
- 📺 **Live video display** (no recording needed)

---

## 🚀 Quick Start

### **Easiest Way** ⭐

**Just double-click:**
```
START_THREAT_DETECTOR.bat
```

### **Alternative: Python Menu**

```bash
python safeguard_visual.py
```

### **Alternative: Direct Command**

```bash
python unified_threat_detector.py
```

---

## 🎮 How to Use

1. **Start the detector** using any method above
2. **TWO VIEWING MODES:**

   **A) Desktop Window Mode** (if OpenCV GUI works):
   - Live video window opens automatically
   - Press 'q' to stop

   **B) Web Browser Mode** (automatic fallback):
   - Browser opens to http://localhost:5000
   - Live video stream in your browser
   - Press Ctrl+C in console to stop

3. **What you'll see:**
   - Colored boxes around people (green=normal, red=threat)
   - Threat labels and timers
   - Real-time statistics
   - Recent alerts

4. **Listen for beep alarms** when threats are detected:
   - Weapon: 3 rapid beeps
   - Falling/Unconscious/Drowning: Long beep
   - Sleeping: Single beep

---

## ⚙️ System Requirements

- **OS:** Windows 10/11
- **Python:** 3.8+
- **RAM:** 4 GB minimum, 8 GB recommended
- **Camera:** Any webcam (720p or higher)

---

## 📦 Installation

```bash
# Install dependencies
pip install ultralytics opencv-python numpy

# Run
python unified_threat_detector.py
```

---

## 🔧 Configuration

Edit `unified_threat_detector.py` to adjust:

```python
class ThreatConfig:
    # Detection thresholds
    SLEEP_DURATION_THRESHOLD = 3.0  # seconds before alert
    FALL_SPEED_THRESHOLD = 0.3      # sensitivity
    UNCONSCIOUS_DURATION = 5.0      # seconds
    WEAPON_CONFIDENCE = 0.6         # 0.0-1.0

    # Alarm settings
    ALARM_ENABLED = True
    ALARM_FREQUENCY = 2500          # Hz (pitch)
    ALARM_DURATION = 500            # ms (length)
    ALARM_COOLDOWN = 3.0            # seconds between alarms
```

---

## 📚 Documentation

- **Full Guide:** `UNIFIED_THREAT_DETECTION_GUIDE.md`
- **Competitors:** `COMPETITORS_AND_MODELS.md`

---

## 🎯 Project Structure

```
projectmit/
├── unified_threat_detector.py    # Main detection system
├── safeguard_visual.py           # Interactive menu launcher
├── START_THREAT_DETECTOR.bat     # Quick launcher (Windows)
├── README.md                      # This file
├── UNIFIED_THREAT_DETECTION_GUIDE.md  # Full documentation
├── backend/                       # Backend API (optional)
├── frontend/                      # Web dashboard (optional)
└── models/                        # AI models (auto-downloaded)
```

---

## 🆘 Troubleshooting

### **No beep sound**
- Check your volume
- Test: `python -c "import winsound; winsound.Beep(2500, 500)"`

### **Can't see video window**
- Make sure OpenCV is installed: `pip install opencv-python`
- The window might be behind other windows - check taskbar

### **Low FPS**
- Close other applications
- The system uses YOLOv8n (fastest model)

### **Weapon not detected**
- Lower the confidence threshold in config
- Ensure good lighting
- Weapon must be clearly visible

---

## ✅ You're Ready!

**Start detecting threats now:**

```
START_THREAT_DETECTOR.bat
```

**Or:**

```bash
python unified_threat_detector.py
```

**Watch the live video window and listen for beep alarms!** 🚀🔊

---

## 👨‍💻 About the Team

### **Asif Ali** - Lead Developer & AI Engineer
- GitHub: [@asifaliattari](https://github.com/asifaliattari)
- Specialization: AI/ML, Computer Vision, Threat Detection Systems
- Role: Lead architecture, YOLOv8 integration, real-time detection pipeline

### **Sharmeen Asif** - Co-Developer & System Architect
- Specialization: Full-stack Development, System Design
- Role: Backend API, frontend integration, deployment infrastructure

**Together, we're building humanitarian AI systems to make the world safer.**

---

## 📄 License

MIT License - see LICENSE file for details

Copyright (c) 2025 Asif Ali & Sharmeen Asif

---

## 🙏 Acknowledgments

- YOLOv8 by Ultralytics
- MediaPipe by Google
- OpenAI GPT-4
- Open source community

---

**Built with ❤️ by Asif Ali & Sharmeen Asif**

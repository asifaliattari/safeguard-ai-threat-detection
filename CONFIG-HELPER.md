# ⚡ SUPER QUICK CONFIG (5 Minutes)

Copy-paste these templates with YOUR keys!

---

## 1️⃣ Frontend Config

**File:** `frontend/.env.local`

```env
# ===== PASTE YOUR KEYS BELOW =====

# Neon Database (from https://neon.tech/)
DATABASE_URL="paste-your-neon-connection-string-here"

# NextAuth Secret (run: openssl rand -base64 32)
NEXTAUTH_SECRET="run-openssl-rand-base64-32-and-paste-result-here"
NEXTAUTH_URL="http://localhost:3000"

# Backend
NEXT_PUBLIC_WS_URL="ws://localhost:8000"
NEXT_PUBLIC_API_URL="http://localhost:8000"

# Claude API (from https://console.anthropic.com/)
ANTHROPIC_API_KEY="paste-your-claude-key-here-starts-with-sk-ant"

# OpenAI (optional - skip for now)
# OPENAI_API_KEY="sk-..."
```

---

## 2️⃣ Backend Config

**File:** `backend/.env`

```env
# ===== PASTE YOUR KEYS BELOW =====

# Same Neon Database URL as frontend
DATABASE_URL="paste-same-neon-connection-string-here"

# Same Claude API key
ANTHROPIC_API_KEY="paste-same-claude-key-here"

# Gmail Settings
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-16-char-gmail-app-password"
SMTP_FROM_EMAIL="SafeGuard AI <your-email@gmail.com>"

# Where to send alerts
ALERT_EMAIL="your-email@gmail.com"

# Frontend URL
FRONTEND_URL="http://localhost:3000"

# Can ignore this for now
ENCRYPTION_KEY="not-needed-for-mvp"
```

---

## ✅ Quick Checklist

- [ ] Got Neon connection string → Paste in BOTH files
- [ ] Got Claude API key → Paste in BOTH files
- [ ] Got Gmail app password → Paste in backend only
- [ ] Updated your-email@gmail.com → Your actual email
- [ ] Saved both files

---

## 🚀 After Config, Run:

### Windows:
```bash
# Double-click QUICK-START.bat
# OR run manually:
cd frontend
npx prisma db push
```

### Then Start:

**Terminal 1:**
```bash
cd backend
venv\Scripts\activate
pip install anthropic aiohttp aiosmtplib
python -m uvicorn app.main:app --reload
```

**Terminal 2:**
```bash
cd frontend
npm run dev
```

**Browser:**
```
http://localhost:3000
```

---

## 🎯 If You Get Stuck

### No Neon account?
- Takes 2 minutes: https://neon.tech/
- Free tier is perfect for MVP

### No Claude key?
- Takes 2 minutes: https://console.anthropic.com/
- $5 free credit included!

### No Gmail app password?
- 2-step verification: https://myaccount.google.com/security
- App passwords: https://myaccount.google.com/apppasswords

### Can't find openssl?
For NEXTAUTH_SECRET, just use any random 32-character string:
```
NEXTAUTH_SECRET="safeguard-ai-super-secret-key-2024-mvp-demo"
```

---

## ⚡ SPEEDRUN MODE (Already have keys?)

1. Update `frontend/.env.local` (30 seconds)
2. Update `backend/.env` (30 seconds)
3. Run: `cd frontend && npx prisma db push` (1 minute)
4. Start backend: `cd backend && venv\Scripts\activate && pip install anthropic aiohttp aiosmtplib && python -m uvicorn app.main:app --reload` (2 minutes)
5. Start frontend: `cd frontend && npm run dev` (30 seconds)
6. Open http://localhost:3000 (instant)

**TOTAL: 5 minutes to running system!**

---

Ready? **Let me know when you have your API keys!**

# 🔑 Get Your API Keys (10 Minutes)

## Required APIs

### 1. Neon Database (FREE) ⭐ REQUIRED
**Time: 2 minutes**

1. Go to https://neon.tech/
2. Sign up with GitHub/Google
3. Create new project: "safeguard-ai"
4. Copy connection string
5. Paste into both `.env` files (frontend & backend)

**Looks like:**
```
postgresql://user:password@ep-xxxxx.aws.neon.tech/neondb?sslmode=require
```

---

### 2. Anthropic Claude (REQUIRED for LLM diagnosis) ⭐
**Time: 2 minutes**
**Cost: $5 free credit, then ~$0.003 per detection**

1. Go to https://console.anthropic.com/
2. Sign up
3. Click "API Keys" → "Create Key"
4. Copy the key (starts with `sk-ant-`)
5. Paste into both `.env` files

**Free tier: $5 credit = ~1,600 detections!**

---

### 3. Gmail App Password (FREE) ⭐ REQUIRED for Email Alerts
**Time: 3 minutes**

1. Go to Google Account settings
2. Enable 2-Step Verification (if not already)
3. Go to https://myaccount.google.com/apppasswords
4. Create app password for "SafeGuard AI"
5. Copy the 16-character password
6. Paste into backend `.env`:
   - `SMTP_USER="your-email@gmail.com"`
   - `SMTP_PASSWORD="xxxx xxxx xxxx xxxx"`

**OR use another email service (optional):**
- SendGrid (free 100/day)
- Mailgun (free 5,000/month)
- AWS SES (free 62,000/month)

---

### 4. OpenAI (OPTIONAL - for RAG chatbot later)
**Time: 2 minutes**
**Cost: ~$0.0001 per message**

1. Go to https://platform.openai.com/api-keys
2. Create API key
3. Copy (starts with `sk-`)
4. Paste into frontend `.env.local`

**Skip for now if you want - we can add later!**

---

## ✅ Checklist

Before proceeding, make sure you have:

- [ ] Neon database connection string
- [ ] Claude API key (`sk-ant-...`)
- [ ] Gmail app password
- [ ] Updated both `.env` files

## 🚀 After You Have Keys

1. Update `frontend/.env.local`
2. Update `backend/.env`
3. Run database migration:
   ```bash
   cd frontend
   npx prisma generate
   npx prisma db push
   ```
4. Tell me "Keys ready!" and I'll continue building!

---

## 💰 Cost Estimate

**For 1000 detections:**
- Neon DB: **FREE** (512MB tier)
- Claude API: **$3** (~$0.003 each)
- Email: **FREE** (Gmail)
- **Total: ~$3/month**

Very affordable for MVP/testing!

# SafeGuard AI - Setup Guide

Complete setup instructions for the AI-Native Video Anomaly Detection System.

## ✅ What We've Built

Phase 1 Foundation is complete:
- ✅ Next.js 14 frontend with TypeScript & Tailwind CSS
- ✅ Vercel AI SDK integrated (ai, openai, anthropic, langchain)
- ✅ FastAPI backend with Python 3.11
- ✅ Prisma database schema with 8 models
- ✅ Git repository initialized
- ✅ Spec-Kit-Plus documentation structure
- ✅ AI-native reusable architecture

## 🚀 Next Steps

### 1. Get API Keys

You'll need the following API keys:

#### Anthropic Claude (Required)
1. Go to https://console.anthropic.com/
2. Create an API key
3. Copy the key (starts with `sk-ant-`)

#### OpenAI (Required)
1. Go to https://platform.openai.com/api-keys
2. Create an API key
3. Copy the key (starts with `sk-`)

#### Neon Postgres (Required)
1. Go to https://neon.tech/
2. Create a free account
3. Create a new project
4. Copy the connection string

### 2. Configure Environment Variables

#### Frontend (.env.local)
```bash
cd frontend
cp .env.example .env.local
```

Edit `frontend/.env.local`:
```bash
# Database
DATABASE_URL="your-neon-connection-string"

# NextAuth
NEXTAUTH_SECRET="run: openssl rand -base64 32"
NEXTAUTH_URL="http://localhost:3000"

# Backend API
NEXT_PUBLIC_WS_URL="ws://localhost:8000"
NEXT_PUBLIC_API_URL="http://localhost:8000"

# AI APIs
OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY="sk-ant-..."

# VAPID Keys (optional, for push notifications)
# Run: cd frontend && npx web-push generate-vapid-keys
NEXT_PUBLIC_VAPID_PUBLIC_KEY=""
VAPID_PRIVATE_KEY=""
```

#### Backend (.env)
```bash
cd backend
cp .env.example .env
```

Edit `backend/.env`:
```bash
# Database
DATABASE_URL="your-neon-connection-string"

# AI API Keys
ANTHROPIC_API_KEY="sk-ant-..."
OPENAI_API_KEY="sk-..."

# Email (optional for MVP)
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-email@gmail.com"
SMTP_PASSWORD="your-gmail-app-password"
SMTP_FROM_EMAIL="SafeGuard AI <your-email@gmail.com>"

# Security - generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ENCRYPTION_KEY="your-generated-key"

# Frontend URL
FRONTEND_URL="http://localhost:3000"
```

### 3. Setup Database

```bash
cd frontend

# Generate Prisma Client
npx prisma generate

# Push schema to database
npx prisma db push

# (Optional) Open Prisma Studio to view database
npx prisma studio
```

### 4. Install Backend Dependencies

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Download AI Models

```bash
cd backend

# Create weights directory
mkdir -p weights

# Download YOLOv8n (will auto-download on first run)
# The model will download automatically when the detection pipeline runs
```

### 6. Run the Application

#### Terminal 1: Frontend
```bash
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

#### Terminal 2: Backend
```bash
cd backend
# Activate venv first if not already activated
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API will be available at: http://localhost:8000
API Docs: http://localhost:8000/api/docs

### 7. Test the Setup

1. Open http://localhost:3000
2. Open http://localhost:8000/health - should see `{"status": "healthy"}`
3. Check API docs at http://localhost:8000/api/docs

## 📁 Project Structure

```
projectmit/
├── frontend/              # Next.js application
│   ├── app/              # App Router pages
│   ├── components/       # Reusable components
│   ├── lib/              # Utility libraries
│   ├── prisma/           # Database schema
│   └── package.json
│
├── backend/              # FastAPI server
│   ├── app/
│   │   ├── main.py      # FastAPI entry point
│   │   ├── config.py    # Configuration
│   │   ├── models/      # AI model wrappers
│   │   ├── core/        # Detection pipeline
│   │   ├── alerts/      # Alert system
│   │   └── api/         # API endpoints
│   ├── weights/         # AI model weights
│   └── requirements.txt
│
├── docs/                # Spec-Kit-Plus documentation
│   ├── specs/           # Feature specifications
│   ├── plans/           # Implementation plans
│   ├── tasks/           # Task breakdowns
│   └── guides/          # User guides
│
└── README.md
```

## 🎯 Development Workflow (Spec-Kit-Plus)

For each new feature:

1. **Specification**: Create `docs/specs/XXX-feature.md`
2. **Plan**: Create `docs/plans/XXX-feature-plan.md`
3. **Tasks**: Create `docs/tasks/XXX-feature-tasks.md`
4. **Implement**: Build with AI-native, reusable components
5. **Test**: Write tests and verify functionality
6. **Document**: Update API docs and user guides

## 🐛 Troubleshooting

### Prisma errors
```bash
cd frontend
npx prisma generate
npx prisma db push --force-reset
```

### Backend import errors
Make sure you activated the virtual environment:
```bash
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

### Port already in use
- Frontend (3000): Change in package.json
- Backend (8000): Change in uvicorn command

### Database connection issues
- Check your DATABASE_URL in both .env files
- Ensure Neon database is running
- Verify connection string includes password

## 📚 Next Development Phases

1. ✅ **Phase 1: Foundation** (COMPLETED)
   - Project setup
   - Database schema
   - Basic server structure

2. **Phase 2: Authentication** (NEXT)
   - NextAuth.js setup
   - Login/Register pages
   - Protected routes

3. **Phase 3: Video Streaming**
   - WebSocket connection
   - Camera access
   - Frame processing

4. **Phase 4: YOLOv8 Detection**
   - Model loading
   - Object detection
   - Bounding box overlay

5. **Phase 5: LLM Diagnosis**
   - Claude integration
   - Severity assessment
   - Alert generation

## 🤝 Contributing

Follow the Spec-Kit-Plus methodology for all contributions:
1. Write specification
2. Create implementation plan
3. Break down into tasks
4. Implement with AI-native patterns
5. Write tests
6. Update documentation

## 📞 Support

- Documentation: `/docs`
- API Reference: http://localhost:8000/api/docs
- Issue Tracker: GitHub Issues (when repository is published)

---

**Status**: Phase 1 Foundation Complete ✅
**Next**: Configure your API keys and database, then proceed to Phase 2!

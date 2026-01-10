# AstolixGen SafeGuard AI

Real-time video anomaly detection system with climate event awareness, LLM-powered diagnosis, and multi-channel alerting.

## 🚀 Features

- **AI-Native Architecture**: Built with Vercel AI SDK, Claude, OpenAI, and LangChain
- **Multi-Source Video**: Phone camera, screen recording, RTSP/HTTP CCTV cameras
- **Real-time Detection**: YOLOv8, TimeSformer, CLIP for comprehensive threat detection
- **LLM Diagnosis**: Claude-powered intelligent analysis and severity assessment
- **Smart Alerts**: Email, push notifications with AI-generated messages
- **RAG Chatbot**: Conversational AI assistant with detection history context
- **Custom Rules**: Natural language detection rule creation
- **PWA**: Mobile-first, installable progressive web app

## 🏗️ Architecture

**Development Methodology**: Spec-Kit-Plus (Specification → Plan → Task → Implement)

**Tech Stack**:
- Frontend: Next.js 14 + TypeScript + Tailwind CSS + Vercel AI SDK
- Backend: FastAPI + Python 3.11 + PyTorch
- Database: Neon Postgres + Prisma + pgvector
- AI: Claude-3.5-Sonnet + OpenAI + LangChain

## 📁 Project Structure

```
astolixgen-safeguard-ai/
├── frontend/          # Next.js application
├── backend/           # FastAPI server
├── docs/             # Spec-Kit-Plus documentation
│   ├── specs/        # Feature specifications
│   ├── plans/        # Implementation plans
│   ├── tasks/        # Task breakdowns
│   ├── api/          # API documentation
│   ├── components/   # Component documentation
│   └── guides/       # User guides
└── shared/           # Shared types
```

## 🛠️ Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL (Neon account)
- API Keys: Anthropic Claude, OpenAI

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your API keys
npm run dev
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
uvicorn app.main:app --reload
```

### Database Setup

```bash
cd frontend
npx prisma generate
npx prisma db push
```

## 📖 Documentation

- **Plan**: `.claude/plans/eager-moseying-galaxy.md`
- **API Docs**: `docs/api/`
- **Component Docs**: `docs/components/`
- **User Guides**: `docs/guides/`

## 🎯 Development Phases

1. ✅ Phase 1: Foundation (Authentication + Basic Detection)
2. ⏳ Phase 2: Multi-Model Detection
3. ⏳ Phase 3: LLM Diagnosis & Alerts
4. ⏳ Phase 4: Custom Rules & RAG Chatbot
5. ⏳ Phase 5: Mobile & PWA
6. ⏳ Phase 6: Production Deployment

## 🤝 Contributing

This project follows the Spec-Kit-Plus methodology:
1. Create a specification in `docs/specs/`
2. Write an implementation plan in `docs/plans/`
3. Break down into tasks in `docs/tasks/`
4. Implement with AI-native, reusable components

## 📝 License

MIT License

## 🏆 Competition

Built for the MIT Climate Change Prize 2025

---

**Powered by**: Claude-3.5-Sonnet, Vercel AI SDK, Next.js, FastAPI

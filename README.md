---
title: TaskFlow Backend API
emoji: 📝
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
license: mit
---

<p align="center">
  <img src="frontend/public/mainpage.png" alt="TaskFlow Landing Page" width="100%" />
</p>

<h1 align="center">TaskFlow</h1>

<p align="center">
  <strong>A Modern Multi-Agent Task Management Application</strong>
</p>

<p align="center">
  <a href="#run-phase-i-console">Phase I Console</a> •
  <a href="#run-phase-ii-web-app">Phase II Web App</a> •
  <a href="#run-phase-iii-ai-chatbot">Phase III AI Chatbot</a> •
  <a href="#live-demo">Live Demo</a> •
  <a href="#oauth-setup">OAuth Setup</a> •
  <a href="#api-reference">API Reference</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-blue?style=flat-square&logo=python" alt="Python" />
  <img src="https://img.shields.io/badge/Next.js-16-black?style=flat-square&logo=next.js" alt="Next.js" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-green?style=flat-square&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/PostgreSQL-Neon-blue?style=flat-square&logo=postgresql" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/TypeScript-5.x-blue?style=flat-square&logo=typescript" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Tailwind-4.0-38B2AC?style=flat-square&logo=tailwind-css" alt="Tailwind" />
</p>

---

## About

**TaskFlow** is a comprehensive multi-agent Todo application built with Spec-Driven Development (SDD). It features both a **console application** (Phase I) and a **full-stack web application** (Phase II), both using the same multi-agent architecture.

**Author**: [Muhammad Qasim](https://github.com/Psqasim) | Full Stack Developer | AI & Web 3.0 Enthusiast

### Project Phases

| Phase | Description | Status | How to Run |
|-------|-------------|--------|------------|
| **Phase I** | Console App (In-Memory) | ✅ Completed | `uv run todo` |
| **Phase II** | Web App (PostgreSQL + OAuth) | ✅ Completed | See below |
| **Phase III** | AI Chatbot (OpenAI Agents SDK) | ✅ Completed | See below |
| **Phase IV** | Local Kubernetes Deployment | ✅ Completed | See [K8s Guide](./docs/PHASE-IV-TESTING-GUIDE.md) |
| Phase V | Cloud Deployment | Upcoming | - |

---

## Live Demo

| Service | URL |
|---------|-----|
| **Web App** | https://hackathon-todo-orcin.vercel.app |
| **Backend API** | https://psqasim-taskflow-backend.hf.space |
| **API Docs** | https://psqasim-taskflow-backend.hf.space/docs |

> **Note**: Backend migrated from Railway to Hugging Face Spaces (free hosting with Docker)

---

## Quick Start

### Prerequisites

- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **UV Package Manager** - [Install](https://docs.astral.sh/uv/)
- **Node.js 20+** (for Phase II) - [Download](https://nodejs.org/)

### Installation

```bash
# Clone the repository
git clone https://github.com/Psqasim/hackathon-todo.git
cd hackathon-todo

# Install Python dependencies
uv sync --all-extras
```

---

## Run Phase I: Console Application

Phase I is a Rich console-based todo app with in-memory storage.

### Start Console App

```bash
uv run todo
```

### Phase I Features

| Feature | Description |
|---------|-------------|
| **Add Task** | Create new tasks with title and description |
| **View Tasks** | List all tasks with status |
| **Update Task** | Edit task title and description |
| **Complete Task** | Mark tasks as done |
| **Delete Task** | Remove tasks |
| **Rich UI** | Beautiful console interface with colors |
| **Multi-Agent** | Orchestrator, TaskManager, StorageHandler agents |

### Phase I Architecture

```
Console App (uv run todo)
    ↓
UIControllerAgent (Rich console)
    ↓
OrchestratorAgent (routes commands)
    ↓
TaskManagerAgent ←→ StorageHandlerAgent
    ↓
InMemoryBackend (data persists only during session)
```

---

## Run Phase II: Full-Stack Web Application

Phase II is a modern web app with authentication, OAuth, and PostgreSQL.

### Backend Setup

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env with your credentials:
#    - DATABASE_URL (Neon PostgreSQL)
#    - JWT_SECRET_KEY
#    - GOOGLE_CLIENT_ID & GOOGLE_CLIENT_SECRET (optional)
#    - GITHUB_CLIENT_ID & GITHUB_CLIENT_SECRET (optional)

# 3. Run backend API
uv run uvicorn src.interfaces.api:app --reload --port 8000
```

### Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Copy environment file
cp .env.example .env.local

# 4. Edit .env.local:
#    NEXT_PUBLIC_API_URL=http://localhost:8000

# 5. Run frontend
npm run dev
```

### Access Points (Local)

| Service | URL |
|---------|-----|
| **Console App** | `uv run todo` |
| **Web Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API Docs (Swagger)** | http://localhost:8000/docs |
| **API Docs (ReDoc)** | http://localhost:8000/redoc |

### Phase II Features

| Feature | Description |
|---------|-------------|
| **User Authentication** | Sign up, sign in, sign out with JWT tokens |
| **OAuth Login** | Google and GitHub social login |
| **Task Management** | Create, read, update, delete tasks |
| **Priority Levels** | Low, Medium, High, Urgent priorities |
| **Due Dates** | Set deadlines for your tasks |
| **Tags** | Organize tasks with up to 10 tags |
| **Search** | Real-time search with debounced input |
| **Task Filtering** | Filter by All, Pending, or Completed |
| **Statistics Dashboard** | Visual stats for task progress |
| **Responsive Design** | Mobile-friendly interface |
| **Modern UI/UX** | Beautiful gradients and animations |

### Phase II Architecture

```
Web Frontend (Next.js 16)
    ↓ REST API
FastAPI Backend
    ↓
TaskManagerAgent ←→ StorageHandlerAgent
    ↓
PostgresBackend (Neon - persistent storage)
```

---

## Run Phase III: AI Chatbot

Phase III adds an AI-powered chatbot using the OpenAI Agents SDK for natural language task management.

### Prerequisites

- All Phase II requirements
- **OpenAI API Key** with credit (gpt-4o-mini recommended, ~$7 minimum)

### Additional Environment Variables

Add to your `.env` file:

```bash
# OpenAI API Key (REQUIRED for chat)
OPENAI_API_KEY=sk-proj-your-key-here
```

### Running Phase III (3 Terminals Required)

```bash
# Terminal 1: Backend API (Port 8000)
uv run uvicorn src.interfaces.api:app --reload --port 8000

# Terminal 2: MCP Server (Port 8001)
uv run python -m src.mcp_server.server

# Terminal 3: Frontend (Port 3000)
cd frontend && npm run dev
```

### Access Chat

1. Open http://localhost:3000
2. Sign in to your account
3. Click **"AI Chat"** in the header
4. Accept the privacy notice (first time only)
5. Start chatting with the AI assistant

### Phase III Features

| Feature | Description |
|---------|-------------|
| **Natural Language Tasks** | "Add a task to buy groceries tomorrow" |
| **Task Queries** | "What tasks are due this week?" |
| **Task Updates** | "Change that to high priority" |
| **Context Awareness** | Remembers conversation history |
| **8 MCP Tools** | Full CRUD + search/filter operations |
| **Privacy Notice** | Transparent data handling disclosure |

### Phase III Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                      │
│  localStorage: conversation_ids only (no message content)   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                         │
│              STATELESS - no chat storage                    │
│         Passes conversation_id to Agent Runner              │
└─────────────────────────┬───────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────────┐
│   Neon PostgreSQL       │     │   OpenAI Conversations API      │
│  ONLY: Users, Tasks     │     │  Stores: Chat history, threads  │
└─────────────────────────┘     └─────────────────────────────────┘
```

**Data Storage:**
| Data | Location |
|------|----------|
| Users, Tasks | PostgreSQL (Neon) |
| Chat History | OpenAI Conversations API (30 days) |
| Conversation IDs | Browser localStorage |

---

## Run Phase IV: Kubernetes Deployment

Phase IV deploys the entire TaskFlow stack to a local Kubernetes cluster (Docker Desktop or Minikube) with production-ready containerization, health probes, and AI-assisted DevOps tooling.

### Prerequisites

- **Docker Desktop** with Kubernetes enabled OR **Minikube**
- **kubectl** CLI (bundled with Docker Desktop)
- **Helm 3.x** (optional, for Helm-based deployment)
- All Docker images built (backend and frontend)

### Deployment Methods

Choose your preferred deployment method:

#### Method 1: Docker Desktop Kubernetes (Recommended)

```bash
# 1. Build Docker images
docker build -t taskflow-backend:latest -f Dockerfile.k8s .
docker build -t taskflow-frontend:latest ./frontend

# 2. Generate secrets
bash scripts/generate-secrets.sh

# 3. Deploy to Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# 4. Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=taskflow-backend -n taskflow --timeout=300s
kubectl wait --for=condition=ready pod -l app=taskflow-frontend -n taskflow --timeout=300s

# 5. Access the application
open http://localhost  # Frontend via LoadBalancer
```

#### Method 2: Minikube

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=4096

# 2. Build and load images
docker build -t taskflow-backend:latest -f Dockerfile.k8s .
docker build -t taskflow-frontend:latest ./frontend
minikube image load taskflow-backend:latest
minikube image load taskflow-frontend:latest

# 3. Deploy (same as Docker Desktop)
kubectl apply -f k8s/

# 4. Access via Minikube
minikube service frontend-service -n taskflow
```

**📖 Full Minikube Guide**: [docs/MINIKUBE-DEPLOYMENT.md](./docs/MINIKUBE-DEPLOYMENT.md)

#### Method 3: Helm Chart (Advanced)

```bash
# Create values file with secrets
cat > values-secrets.yaml <<EOF
secrets:
  databaseUrl: "postgresql://..."
  jwtSecretKey: "your-secret"
  openaiApiKey: "sk-..."
  # ... other secrets
EOF

# Install with Helm
helm install taskflow ./helm/taskflow -f values-secrets.yaml

# Access the application
kubectl get svc frontend-service -n taskflow
```

**📖 Helm Chart Guide**: [helm/taskflow/README.md](./helm/taskflow/README.md)

### Phase IV Features

| Feature | Description |
|---------|-------------|
| **Docker Multi-Stage Builds** | Optimized images: Backend 561MB, Frontend 289MB |
| **Kubernetes Orchestration** | Deployments, Services, ConfigMaps, Secrets |
| **Health Probes** | Liveness, Readiness, Startup probes for auto-healing |
| **Resource Management** | CPU/Memory limits and requests |
| **Non-Root Security** | All containers run as UID 1000 |
| **LoadBalancer Service** | External access to frontend |
| **ClusterIP Service** | Internal backend communication |
| **Helm Chart** | One-command deployment with customizable values |
| **AI-Assisted DevOps** | Docker AI, kubectl-ai, Kagent for optimization |

### Phase IV Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Desktop / Minikube                    │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              Namespace: taskflow                       │   │
│  │                                                        │   │
│  │  ┌──────────────────────┐  ┌──────────────────────┐  │   │
│  │  │  Backend Deployment  │  │ Frontend Deployment  │  │   │
│  │  │  (replica: 1)        │  │ (replica: 1)         │  │   │
│  │  │  - FastAPI: 7860     │  │ - Next.js: 3000      │  │   │
│  │  │  - MCP Server: 8001  │  │ - Standalone output  │  │   │
│  │  │  - Health probes     │  │ - Health probes      │  │   │
│  │  │  - Resources: 500Mi  │  │ - Resources: 512Mi   │  │   │
│  │  └──────────┬───────────┘  └──────────┬───────────┘  │   │
│  │             │                          │              │   │
│  │  ┌──────────▼───────┐      ┌──────────▼───────────┐ │   │
│  │  │ Backend Service  │      │ Frontend Service     │ │   │
│  │  │ (ClusterIP:8000) │      │ (LoadBalancer:80)    │ │   │
│  │  └──────────────────┘      └──────────────────────┘ │   │
│  │                                      │               │   │
│  └──────────────────────────────────────┼───────────────┘   │
│                                         │                    │
└─────────────────────────────────────────┼────────────────────┘
                                          │
                                          ▼
                                   http://localhost
```

### AI DevOps Tools Used

Phase IV leveraged AI-powered tools to accelerate development:

| Tool | Purpose | Impact |
|------|---------|--------|
| **Docker AI (Gordon)** | Dockerfile optimization, multi-stage builds | 43% image size reduction |
| **kubectl-ai** | K8s manifest generation, resource recommendations | 2-3 hours saved |
| **Kagent** | Cluster analysis, security audit, optimization | 85% first-deployment success |

**Time Saved**: 9-16 hours total (~60-70% reduction)

**📖 Full AI Tools Guide**: [docs/AI-DEVOPS-TOOLS.md](./docs/AI-DEVOPS-TOOLS.md)
**📖 AI Research Report**: [specs/004-k8s-deployment/ai-tools-research.md](./specs/004-k8s-deployment/ai-tools-research.md)

### Testing Guide

**📖 Complete Testing Guide**: [docs/PHASE-IV-TESTING-GUIDE.md](./docs/PHASE-IV-TESTING-GUIDE.md)

Includes:
- Prerequisites verification
- Build instructions
- Deployment steps
- Verification commands
- Troubleshooting
- Performance benchmarks

---

## All Four Phases Use Same Codebase

| Aspect | Phase I (Console) | Phase II (Web) | Phase III (AI Chat) | Phase IV (Kubernetes) |
|--------|-------------------|----------------|---------------------|----------------------|
| **Entry Point** | `uv run todo` | `uvicorn + npm run dev` | + MCP Server | `kubectl apply -f k8s/` |
| **Interface** | Rich Console | Next.js Web UI | AI Chat Page | Same as II + III |
| **Storage** | InMemoryBackend | PostgresBackend (Neon) | + OpenAI Conversations | Same as II + III |
| **Auth** | None | JWT + OAuth | Same as Phase II | Same as II + III |
| **AI** | None | None | OpenAI Agents SDK | Same as III + AI DevOps |
| **Deployment** | Local | Local/Vercel/HF | Same as Phase II | Kubernetes Cluster |
| **Can Run Together** | Yes | Yes | Yes | Yes (via K8s) |

### Run All Simultaneously

```bash
# Terminal 1: Phase I Console
uv run todo

# Terminal 2: Backend API (serves Phase II + III)
uv run uvicorn src.interfaces.api:app --reload --port 8000

# Terminal 3: MCP Server (Phase III only)
uv run python -m src.mcp_server.server

# Terminal 4: Frontend (serves Phase II + III)
cd frontend && npm run dev
```

---

## Environment Variables

### Backend (`.env`)

```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require

# JWT Authentication
JWT_SECRET_KEY=your-32-character-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# OAuth - Google (optional)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OAuth - GitHub (optional)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### Frontend (`frontend/.env.local`)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## OAuth Setup

### Google OAuth

1. **Go to** [Google Cloud Console](https://console.cloud.google.com/)
2. **Create Project** → Name it "TaskFlow"
3. **OAuth Consent Screen** → Select "External" → Fill in app name
4. **Create Credentials** → "OAuth client ID" → "Web application"
5. **Add URIs**:
   - Authorized JavaScript origins: `http://localhost:3000`
   - Authorized redirect URIs: `http://localhost:8000/api/auth/google/callback`
6. **Copy** Client ID and Client Secret to `.env`

### GitHub OAuth

1. **Go to** [GitHub Developer Settings](https://github.com/settings/developers)
2. **New OAuth App**
3. **Fill in**:
   - Application name: `TaskFlow`
   - Homepage URL: `http://localhost:3000`
   - Authorization callback URL: `http://localhost:8000/api/auth/github/callback`
4. **Copy** Client ID and Client Secret to `.env`

---

## API Reference

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/signup` | Create new account |
| `POST` | `/api/auth/signin` | Sign in with email/password |
| `POST` | `/api/auth/signout` | Sign out |
| `GET` | `/api/auth/me` | Get current user |
| `GET` | `/api/auth/google` | Start Google OAuth |
| `GET` | `/api/auth/github` | Start GitHub OAuth |

### Task Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users/{user_id}/tasks` | List tasks |
| `POST` | `/api/users/{user_id}/tasks` | Create task |
| `GET` | `/api/users/{user_id}/tasks/{task_id}` | Get task |
| `PUT` | `/api/users/{user_id}/tasks/{task_id}` | Update task |
| `DELETE` | `/api/users/{user_id}/tasks/{task_id}` | Delete task |
| `PATCH` | `/api/users/{user_id}/tasks/{task_id}/complete` | Toggle complete |

### Health Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Basic health check |
| `GET` | `/api/health/db` | Database connection check |

---

## Testing

### Run Backend Tests

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=term-missing
```

### Code Quality

```bash
# Linting
uv run ruff check src tests

# Type checking
uv run mypy src
```

---

## Technology Stack

### Backend
| Technology | Purpose |
|------------|---------|
| Python 3.12+ | Language |
| FastAPI | Web Framework |
| SQLModel | ORM |
| PostgreSQL (Neon) | Database |
| JWT (python-jose) | Authentication |
| Passlib + bcrypt | Password Hashing |
| Rich | Console UI (Phase I) |

### Frontend
| Technology | Purpose |
|------------|---------|
| Next.js 16 | React Framework |
| TypeScript | Language |
| React 19 | UI Library |
| Tailwind CSS 4 | Styling |

---

## Project Structure

```
hackathon-todo/
├── src/                          # Backend source
│   ├── agents/                   # Multi-agent architecture
│   │   ├── orchestrator.py       # Routes commands
│   │   ├── task_manager.py       # Business logic
│   │   ├── storage_handler.py    # Data operations
│   │   └── ui_controller.py      # Console UI (Phase I)
│   ├── mcp_server/               # MCP server (Phase III)
│   │   ├── server.py             # MCP server entry
│   │   ├── agent.py              # TaskAgent with OpenAI
│   │   ├── tools.py              # 8 MCP tools
│   │   └── backend_client.py     # HTTP client for FastAPI
│   ├── backends/                 # Storage backends
│   │   ├── memory.py             # InMemoryBackend (Phase I)
│   │   └── postgres.py           # PostgresBackend (Phase II)
│   ├── auth/                     # JWT & password handling
│   ├── interfaces/api.py         # FastAPI REST API
│   ├── app.py                    # Console app entry (Phase I)
│   └── config.py                 # Environment settings
├── frontend/                     # Next.js frontend (Phase II)
│   ├── app/                      # App Router pages
│   ├── components/               # React components
│   └── lib/                      # API client
├── tests/                        # Test suites
├── specs/                        # Feature specifications
├── docs/                         # Documentation
│   ├── DEPLOYMENT.md             # Complete deployment guide
│   ├── HUGGINGFACE_DEPLOYMENT.md # HF Spaces specific guide
│   └── PHASE-*-TESTING-GUIDE.md  # Testing guides
├── Dockerfile                    # Docker config for HF Spaces
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## WSL Troubleshooting

If you encounter SWC compiler issues in WSL:

```bash
cd frontend
rm -rf node_modules/.cache .next
npm install @next/swc-linux-x64-gnu --force
npm run dev
```

---

## License

MIT License - feel free to use this project for learning and development.

---

<p align="center">
  <strong>Built by Muhammad Qasim</strong>
</p>

<p align="center">
  <a href="https://github.com/Psqasim">
    <img src="https://img.shields.io/badge/GitHub-Psqasim-181717?style=flat-square&logo=github" alt="GitHub" />
  </a>
  <a href="https://www.linkedin.com/in/muhammad-qasim-5bba592b4/">
    <img src="https://img.shields.io/badge/LinkedIn-Muhammad%20Qasim-0A66C2?style=flat-square&logo=linkedin" alt="LinkedIn" />
  </a>
  <a href="https://x.com/psqasim0">
    <img src="https://img.shields.io/badge/Twitter-@psqasim0-1DA1F2?style=flat-square&logo=twitter" alt="Twitter" />
  </a>
</p>

<p align="center">
  Built with Spec-Driven Development (SDD) and Claude Code
</p>

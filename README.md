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
| **Phase I** | Console App (In-Memory) | Completed | `uv run todo` |
| **Phase II** | Web App (PostgreSQL + OAuth) | Completed | See below |
| Phase III | AI Chatbot (MCP Integration) | Upcoming | - |
| Phase IV | Local Kubernetes | Upcoming | - |
| Phase V | Cloud Deployment | Upcoming | - |

---

## Live Demo

| Service | URL |
|---------|-----|
| **Web App** | https://hackathon-todo-orcin.vercel.app |
| **Backend API** | https://web-production-3e6df.up.railway.app |
| **API Docs** | https://web-production-3e6df.up.railway.app/docs |

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

## Both Phases Use Same Codebase

| Aspect | Phase I (Console) | Phase II (Web) |
|--------|-------------------|----------------|
| **Entry Point** | `uv run todo` | `uvicorn + npm run dev` |
| **Interface** | Rich Console | Next.js Web UI |
| **Storage** | InMemoryBackend | PostgresBackend (Neon) |
| **Auth** | None | JWT + OAuth |
| **Agents** | Same (Orchestrator, TaskManager, StorageHandler) | Same |
| **Can Run Together** | Yes | Yes |

### Run Both Simultaneously

```bash
# Terminal 1: Phase I Console
uv run todo

# Terminal 2: Phase II Backend
uv run uvicorn src.interfaces.api:app --reload --port 8000

# Terminal 3: Phase II Frontend
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
├── railway.json                  # Railway deployment config
├── Procfile                      # Process file for deployment
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

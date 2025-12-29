<p align="center">
  <img src="frontend/public/mainpage.png" alt="TaskFlow Landing Page" width="100%" />
</p>

<h1 align="center">TaskFlow</h1>

<p align="center">
  <strong>A Modern Full-Stack Task Management Application</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#oauth-setup">OAuth Setup</a> •
  <a href="#api-reference">API Reference</a> •
  <a href="#testing">Testing</a>
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

**TaskFlow** is a comprehensive multi-agent Todo application built with Spec-Driven Development (SDD). It features a beautiful modern UI, secure authentication with OAuth support, and a robust FastAPI backend.

**Author**: [Muhammad Qasim](https://github.com/Psqasim) | Full Stack Developer | AI & Web 3.0 Enthusiast

### Project Phases

| Phase | Description | Status |
|-------|-------------|--------|
| Phase I | Console App (In-Memory) | Completed |
| **Phase II** | **Web App (PostgreSQL + OAuth)** | **Current** |
| Phase III | AI Chatbot (MCP Integration) | Upcoming |
| Phase IV | Local Kubernetes | Upcoming |
| Phase V | Cloud Deployment | Upcoming |

---

## Features

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

---

## Quick Start

### Prerequisites

- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **UV Package Manager** - [Install](https://docs.astral.sh/uv/)
- **Node.js 20+** - [Download](https://nodejs.org/)
- **PostgreSQL** - We recommend [Neon](https://neon.tech) (free serverless PostgreSQL)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Psqasim/hackathon-todo.git
cd hackathon-todo

# 2. Install backend dependencies
uv sync --all-extras

# 3. Install frontend dependencies
cd frontend && npm install && cd ..

# 4. Copy environment files
cp .env.example .env
cp frontend/.env.example frontend/.env.local
```

### Environment Variables

#### Backend (`.env` in project root)

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

#### Frontend (`frontend/.env.local`)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Running the Application

Open **two terminals** from the project root:

**Terminal 1 - Backend (FastAPI)**
```bash
uv run uvicorn src.interfaces.api:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend (Next.js)**
```bash
cd frontend && npm run dev
```

### Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |

---

## OAuth Setup

### Google OAuth

1. **Go to** [Google Cloud Console](https://console.cloud.google.com/)
2. **Create Project** - Click project dropdown → "New Project" → Name it "TaskFlow"
3. **OAuth Consent Screen**
   - Go to "APIs & Services" → "OAuth consent screen"
   - Select "External" → Fill in app name, email → Save
4. **Create Credentials**
   - Go to "Credentials" → "Create Credentials" → "OAuth client ID"
   - Application type: "Web application"
   - Authorized JavaScript origins: `http://localhost:3000`
   - Authorized redirect URIs: `http://localhost:8000/api/auth/google/callback`
5. **Copy** Client ID and Client Secret to your `.env` file

### GitHub OAuth

1. **Go to** [GitHub Developer Settings](https://github.com/settings/developers)
2. **New OAuth App** - Click "New OAuth App"
3. **Fill in details**:
   - Application name: `TaskFlow`
   - Homepage URL: `http://localhost:3000`
   - Authorization callback URL: `http://localhost:8000/api/auth/github/callback`
4. **Register** and copy Client ID
5. **Generate** Client Secret and copy it
6. **Add both** to your `.env` file

### Verify OAuth

1. Start backend and frontend
2. Go to http://localhost:3000/signin
3. Click "Google" or "GitHub" button
4. Authorize the app
5. You'll be redirected to the dashboard

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
| `GET` | `/api/users/{user_id}/tasks` | List tasks (filter: `?status=pending`) |
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

# With verbose output
uv run pytest -v

# With coverage report
uv run pytest --cov=src --cov-report=term-missing

# HTML coverage report
uv run pytest --cov=src --cov-report=html
# Open htmlcov/index.html
```

### Test API with cURL

```bash
# Health check
curl http://localhost:8000/health

# Create user
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123","name":"Test User"}'

# Sign in (save the token)
curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123"}'
```

### Test Frontend Manually

1. Open http://localhost:3000
2. Click "Get Started" → Create account
3. Create a task with title, description, priority
4. Mark task as complete
5. Edit and delete tasks
6. Test search functionality
7. Sign out and sign back in

### Code Quality

```bash
# Linting
uv run ruff check src tests

# Auto-fix
uv run ruff check --fix src tests

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
| Pydantic v2 | Validation |
| structlog | Logging |
| httpx | OAuth HTTP Client |

### Frontend
| Technology | Purpose |
|------------|---------|
| Next.js 16 | React Framework |
| TypeScript | Language |
| React 19 | UI Library |
| Tailwind CSS 4 | Styling |
| Zod | Validation |

---

## Project Structure

```
hackathon-todo/
├── src/                          # Backend source
│   ├── auth/                     # JWT & password handling
│   ├── agents/                   # Multi-agent architecture
│   ├── models/                   # Pydantic/SQLModel models
│   ├── backends/                 # Storage backends
│   ├── interfaces/api.py         # FastAPI REST API
│   ├── config.py                 # Environment settings
│   └── db.py                     # Database connection
├── frontend/                     # Next.js frontend
│   ├── app/                      # App Router pages
│   ├── components/               # React components
│   ├── lib/                      # Utilities
│   └── public/                   # Static assets
├── tests/                        # Test suites
├── specs/                        # Feature specifications
├── .env.example                  # Environment template
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

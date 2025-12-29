# Quickstart Guide: Full-Stack Web Application (Phase II)

**Feature Branch**: `002-fullstack-web-app`
**Date**: 2025-12-28

## Prerequisites

- Python 3.12+ installed
- Node.js 18+ installed
- UV package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Neon account (free tier: https://neon.tech)
- Git configured

## 1. Database Setup (Neon)

### Create Database

1. Sign in to https://console.neon.tech
2. Create new project: "hackathon-todo"
3. Copy connection string (will look like):
   ```
   postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```

### Verify Connection

```bash
# Test connection (optional)
psql "postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require"
```

## 2. Backend Setup

### Install Dependencies

```bash
cd hackathon-todo

# Add Phase II dependencies
uv add fastapi uvicorn[standard] sqlmodel psycopg2-binary python-jose[cryptography] python-multipart
```

### Configure Environment

Create `.env` file in project root:

```env
# Database
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require

# Authentication (generate a secure secret)
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-here

# CORS
FRONTEND_URL=http://localhost:3000
```

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Start Backend Server

```bash
# Development mode with auto-reload
uv run uvicorn src.interfaces.api:app --reload --port 8000
```

Verify at: http://localhost:8000/docs

## 3. Frontend Setup

### Initialize Next.js Project

```bash
# Create frontend directory
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --app \
  --no-src-dir \
  --import-alias "@/*"

cd frontend
```

### Install Dependencies

```bash
npm install better-auth zod
```

### Configure Environment

Create `frontend/.env.local`:

```env
# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth (same secret as backend!)
BETTER_AUTH_SECRET=your-secret-key-min-32-chars-here
BETTER_AUTH_URL=http://localhost:3000
```

### Start Frontend Server

```bash
cd frontend
npm run dev
```

Visit: http://localhost:3000

## 4. Running Both Apps

Open two terminals:

**Terminal 1 - Backend:**
```bash
cd hackathon-todo
uv run uvicorn src.interfaces.api:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd hackathon-todo/frontend
npm run dev
```

**Terminal 3 - Phase I Console (still works!):**
```bash
cd hackathon-todo
uv run todo
```

## 5. Testing the Setup

### Backend Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### Database Connection Test

```bash
curl http://localhost:8000/api/health/db
# Expected: {"status": "connected"}
```

### Full Authentication Flow

```bash
# 1. Sign up
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "name": "Test User", "password": "password123"}'

# 2. Sign in (get token)
TOKEN=$(curl -X POST http://localhost:8000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}' \
  | jq -r '.token')

# 3. Create task
curl -X POST http://localhost:8000/api/users/USER_ID/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task"}'
```

## 6. Directory Structure After Setup

```
hackathon-todo/
├── .env                      # Backend environment variables
├── pyproject.toml            # Python dependencies (updated)
├── src/                      # Python backend
│   ├── agents/               # Reused from Phase I
│   ├── backends/
│   │   ├── memory.py         # Phase I (still used by console)
│   │   └── postgres.py       # NEW: PostgreSQL backend
│   ├── interfaces/
│   │   ├── console.py        # Phase I console
│   │   └── api.py            # NEW: FastAPI application
│   └── models/
│       ├── tasks.py          # Updated with user_id
│       └── user.py           # NEW: User model
├── frontend/                 # NEW: Next.js application
│   ├── .env.local            # Frontend environment
│   ├── app/
│   │   ├── page.tsx          # Landing page
│   │   ├── signup/
│   │   ├── signin/
│   │   └── dashboard/
│   ├── components/
│   ├── lib/
│   │   ├── auth.ts           # Better Auth config
│   │   └── api-client.ts     # Backend API client
│   └── middleware.ts         # Route protection
└── tests/
    └── integration/
        └── api/              # NEW: API tests
```

## 7. Troubleshooting

### Common Issues

**Database Connection Failed**
```
Error: could not connect to server
```
Solution: Check DATABASE_URL, ensure Neon project is active, verify SSL mode.

**CORS Error**
```
Access to fetch has been blocked by CORS policy
```
Solution: Ensure FRONTEND_URL in backend `.env` matches frontend origin.

**JWT Invalid**
```
Error: Invalid or expired token
```
Solution: Verify BETTER_AUTH_SECRET is identical in both `.env` files.

**Port Already in Use**
```bash
# Find and kill process on port 8000
lsof -i :8000
kill -9 <PID>
```

## 8. Development Workflow

1. **Make backend changes** → API auto-reloads (uvicorn --reload)
2. **Make frontend changes** → Next.js hot-reloads automatically
3. **Run tests** → `uv run pytest` (backend), `npm test` (frontend)
4. **Check types** → `uv run mypy src` (backend), `npm run type-check` (frontend)

## 9. Next Steps

After setup is verified:

1. Run `/sp.tasks` to generate implementation tasks
2. Implement features following task order
3. Run tests after each implementation
4. Commit with proper messages

# TaskFlow Deployment Guide

Complete guide for deploying TaskFlow backend and frontend to production.

## Overview

TaskFlow uses a **3-tier deployment architecture**:

1. **Backend API** - Hugging Face Spaces (Docker) - FREE
2. **Frontend** - Vercel (Next.js) - FREE
3. **Database** - Neon PostgreSQL - FREE tier available

## Table of Contents

- [Local Development](#local-development)
- [Hugging Face Spaces Deployment](#hugging-face-spaces-deployment)
- [Vercel Deployment](#vercel-deployment)
- [Neon PostgreSQL Setup](#neon-postgresql-setup)
- [OAuth Configuration](#oauth-configuration)
- [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites

- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **UV Package Manager** - [Install](https://docs.astral.sh/uv/)
- **Node.js 20+** - [Download](https://nodejs.org/)
- **PostgreSQL** (optional, for Phase II+) - Use Neon cloud or local install

### Phase I: Console App (In-Memory)

```bash
# Install dependencies
uv sync --all-extras

# Run console app
uv run todo
```

**Features**: Rich console UI, in-memory storage (data lost on exit)

### Phase II: Web App (PostgreSQL + OAuth)

**Terminal 1 - Backend**:
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials:
# - DATABASE_URL (Neon PostgreSQL)
# - JWT_SECRET_KEY (generate with: openssl rand -hex 32)
# - GOOGLE_CLIENT_ID/SECRET (optional)
# - GITHUB_CLIENT_ID/SECRET (optional)

# Run FastAPI backend
uv run uvicorn src.interfaces.api:app --reload --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env.local

# Edit .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Run Next.js frontend
npm run dev
```

**Access**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Phase III: AI Chatbot (OpenAI + MCP)

Requires Phase II + OpenAI API key.

**Terminal 1 - Backend** (same as Phase II)

**Terminal 2 - MCP Server**:
```bash
# Add to .env:
# OPENAI_API_KEY=sk-proj-xxx
# MCP_BACKEND_URL=http://localhost:8000

# Run MCP server
uv run python -m src.mcp_server.server
```

**Terminal 3 - Frontend** (same as Phase II)

**Access**: Open http://localhost:3000 → Click "AI Chat"

---

## Hugging Face Spaces Deployment

Deploy the backend API to Hugging Face Spaces for **free Docker hosting**.

### Step 1: Create Hugging Face Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Fill in:
   - **Space name**: `taskflow-backend` (or your choice)
   - **License**: MIT
   - **SDK**: Docker
   - **Visibility**: Public or Private
4. Click **"Create Space"**

### Step 2: Prepare Backend Code

Your repository is already configured for HF Spaces:

- ✅ `Dockerfile` - Multi-service container (FastAPI + MCP)
- ✅ `requirements.txt` - All Python dependencies
- ✅ `README.md` - Includes HF YAML frontmatter
- ✅ `src/` - Backend code

**Key Configuration** (already in README.md):
```yaml
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
```

### Step 3: Push to Hugging Face

**Option A: Using Git** (recommended):

```bash
# Add HF remote (if not already added)
git remote add huggingface https://huggingface.co/spaces/YOUR_USERNAME/taskflow-backend

# Create deployment branch (backend only, no frontend)
git checkout -b hf-deploy

# Remove frontend to avoid binary files
git rm -r frontend/

# Commit
git commit -m "chore: prepare backend-only deployment for HF Spaces"

# Push to HF
git push huggingface hf-deploy:main --force
```

**Option B: Using HF Web Interface**:

1. Clone your Space repository
2. Copy backend files (src/, Dockerfile, requirements.txt, README.md)
3. Commit and push

### Step 4: Configure Environment Variables

In your HF Space:

1. Go to **Settings** → **Repository secrets**
2. Add the following secrets:

**Required**:
```bash
DATABASE_URL=postgresql://user:pass@ep-xxx.aws.neon.tech/neondb?sslmode=require
JWT_SECRET_KEY=<32-character-secret-key>
OPENAI_API_KEY=sk-proj-xxx
FRONTEND_URL=https://your-app.vercel.app
BACKEND_URL=https://your-username-taskflow-backend.hf.space
```

**Optional (OAuth)**:
```bash
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GITHUB_CLIENT_ID=xxx
GITHUB_CLIENT_SECRET=xxx
```

**MCP Configuration** (auto-configured):
```bash
MCP_SERVER_PORT=8001
MCP_BACKEND_URL=http://localhost:7860
```

**Note**: `MCP_BACKEND_URL` defaults to `http://localhost:7860` in HF Spaces (internal container call). No need to set it.

### Step 5: Monitor Build

1. Go to your Space dashboard
2. Check **"Logs"** tab
3. Watch build progress (~5-10 minutes first time)

**Build Stages**:
```
1. Cloning repository
2. Building Docker image
   - Installing system dependencies
   - Installing Python packages (pip)
   - Copying backend code
3. Starting container
   - FastAPI on port 7860
   - MCP Server on port 8001
4. Running health checks
5. Space ready!
```

### Step 6: Verify Deployment

```bash
# Health check
curl https://your-username-taskflow-backend.hf.space/health
# Expected: {"status":"healthy"}

# Database health
curl https://your-username-taskflow-backend.hf.space/api/health/db
# Expected: {"status":"connected"}

# API docs (browser)
https://your-username-taskflow-backend.hf.space/docs
```

### Common HF Spaces Issues

**Issue**: Build fails with "binary files rejected"
**Solution**: Remove frontend folder (contains images). Use backend-only branch.

**Issue**: "Failed to connect to backend" in MCP tools
**Solution**: MCP server defaults to `http://localhost:7860`. No config needed.

**Issue**: "Your space is in error"
**Solution**: Check Logs tab. Usually missing environment variables (DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY).

**Issue**: Port binding error
**Solution**: Dockerfile must expose port 7860 (HF requirement).

---

## Vercel Deployment

Deploy the Next.js frontend to Vercel for **free hosting**.

### Step 1: Prepare Frontend

Your frontend is already configured for Vercel:

- ✅ `frontend/` - Next.js 16 App Router
- ✅ `frontend/next.config.ts` - Vercel-optimized
- ✅ `frontend/.env.example` - Environment template

### Step 2: Deploy to Vercel

**Option A: Using Vercel CLI**:

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend
cd frontend

# Deploy
vercel

# Follow prompts:
# - Link to existing project or create new
# - Select frontend/ as root directory
# - Framework: Next.js
# - Build: npm run build
# - Output: .next
```

**Option B: Using Vercel Dashboard**:

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
5. Click **"Deploy"**

### Step 3: Configure Environment Variables

In Vercel Dashboard:

1. Go to **Project Settings** → **Environment Variables**
2. Add:

```bash
NEXT_PUBLIC_API_URL=https://your-username-taskflow-backend.hf.space
```

### Step 4: Verify Deployment

1. Vercel will provide a URL: `https://your-app.vercel.app`
2. Visit the URL
3. Test:
   - Sign up / Sign in
   - Create tasks
   - Use AI chat

---

## Neon PostgreSQL Setup

Use Neon for **free serverless PostgreSQL** hosting.

### Step 1: Create Neon Account

1. Go to [Neon Console](https://console.neon.tech/)
2. Sign up with GitHub/Google
3. Create a new project

### Step 2: Get Connection String

1. Go to **Dashboard** → **Connection Details**
2. Select **"Pooled connection"** (recommended)
3. Copy the connection string:

```
postgresql://user:password@ep-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### Step 3: Initialize Database

Tables are created automatically on first run:

```python
# src/db.py creates tables using SQLModel
def create_tables():
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
```

**Tables Created**:
- `users` - User accounts (JWT auth)
- `tasks` - Task data
- `conversations` - Chat conversations (Phase III)
- `messages` - Chat messages (Phase III)

### Step 4: Verify Connection

```bash
# Test connection (local)
uv run python -c "from src.db import get_engine; print('Connected!' if get_engine() else 'Failed')"
```

### Neon Free Tier Limits

- **Storage**: 0.5 GB
- **Compute**: Shared CPU
- **Branches**: 10
- **Idle timeout**: Suspends after 5 min inactivity
- **Perfect for**: Side projects, demos, prototypes

---

## OAuth Configuration

Configure Google and GitHub OAuth for social login.

### Google OAuth Setup

1. **Create Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project: "TaskFlow"

2. **Enable OAuth**:
   - Go to **APIs & Services** → **OAuth consent screen**
   - Select **"External"**
   - Fill in:
     - App name: TaskFlow
     - User support email: your-email@example.com
     - Developer contact: your-email@example.com
   - Save

3. **Create Credentials**:
   - Go to **Credentials** → **Create Credentials** → **OAuth client ID**
   - Application type: **Web application**
   - Name: TaskFlow Web Client
   - **Authorized JavaScript origins**:
     - `http://localhost:3000` (local)
     - `https://your-app.vercel.app` (production)
   - **Authorized redirect URIs**:
     - `http://localhost:8000/api/auth/google/callback` (local)
     - `https://your-username-taskflow-backend.hf.space/api/auth/google/callback` (production)
   - Save

4. **Copy Credentials**:
   - Copy **Client ID** and **Client Secret**
   - Add to `.env` (local) or HF Space secrets (production)

### GitHub OAuth Setup

1. **Create OAuth App**:
   - Go to [GitHub Developer Settings](https://github.com/settings/developers)
   - Click **"New OAuth App"**
   - Fill in:
     - Application name: TaskFlow
     - Homepage URL: `https://your-app.vercel.app`
     - Authorization callback URL: `https://your-username-taskflow-backend.hf.space/api/auth/github/callback`
   - Register application

2. **Copy Credentials**:
   - Copy **Client ID**
   - Generate **Client Secret**
   - Add to `.env` (local) or HF Space secrets (production)

3. **For Local Dev**:
   - Create separate OAuth app for localhost
   - Callback URL: `http://localhost:8000/api/auth/github/callback`

---

## Troubleshooting

### Backend Issues

**Error**: "Database connection failed"
**Cause**: Invalid `DATABASE_URL` or Neon database not accessible
**Solution**:
- Verify connection string format includes `?sslmode=require`
- Check Neon dashboard for database status
- Test connection locally first

**Error**: "MCP server failed to connect"
**Cause**: Wrong backend URL (port 8000 instead of 7860 in HF)
**Solution**:
- In HF Spaces, MCP server auto-detects `http://localhost:7860`
- For local dev, set `MCP_BACKEND_URL=http://localhost:8000` in `.env`
- Check backend_client.py for correct URL logic

**Error**: "JWT token invalid"
**Cause**: Missing or incorrect `JWT_SECRET_KEY`
**Solution**:
- Generate new secret: `openssl rand -hex 32`
- Add to environment variables
- Restart backend

**Error**: "CORS errors from frontend"
**Cause**: Frontend URL not in ALLOWED_ORIGINS
**Solution**:
- Check `src/config.py` ALLOWED_ORIGINS includes frontend URL
- Add Vercel URL to list
- Restart backend

### Frontend Issues

**Error**: "Failed to fetch" or "Network error"
**Cause**: Wrong `NEXT_PUBLIC_API_URL`
**Solution**:
- Verify API URL in environment variables
- Check backend is running and accessible
- Test backend health endpoint manually

**Error**: "OAuth callback failed"
**Cause**: Wrong redirect URI in OAuth provider
**Solution**:
- Verify redirect URIs in Google/GitHub match backend URL exactly
- Include `/api/auth/google/callback` path
- Use HTTPS for production (HTTP for localhost only)

**Error**: "Hydration error" in Next.js
**Cause**: Server/client mismatch
**Solution**:
- Clear `.next` cache: `rm -rf .next`
- Rebuild: `npm run build`
- Check for async state issues in components

### Database Issues

**Error**: "Too many connections"
**Cause**: Connection pool exhausted
**Solution**:
- Use pooled connection string from Neon
- Check for connection leaks (always close sessions)
- Reduce `connect_args` pool size if needed

**Error**: "SSL connection required"
**Cause**: Missing `?sslmode=require` in connection string
**Solution**:
- Add `?sslmode=require` to DATABASE_URL
- Neon requires SSL connections

**Error**: "Relation does not exist"
**Cause**: Tables not created
**Solution**:
- Tables auto-create on first backend start
- Manually create: `uv run python -c "from src.db import create_tables; create_tables()"`
- Check database logs in Neon console

---

## Production Checklist

Before going to production:

### Security
- [ ] Generate strong JWT_SECRET_KEY (32+ characters)
- [ ] Use environment variables (never commit secrets)
- [ ] Enable HTTPS (Vercel/HF Spaces handle this)
- [ ] Configure CORS properly (only allow your frontend)
- [ ] Review OAuth scopes (minimal required only)

### Performance
- [ ] Enable Neon pooled connection
- [ ] Set appropriate database pool size
- [ ] Use Next.js Image optimization
- [ ] Enable Vercel edge caching
- [ ] Test with realistic data volume

### Monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Monitor API response times
- [ ] Check database query performance
- [ ] Track OpenAI API usage/costs
- [ ] Set up uptime monitoring

### Documentation
- [ ] Update README with production URLs
- [ ] Document OAuth setup steps
- [ ] Create user guide
- [ ] Write API documentation
- [ ] Add troubleshooting guide

---

## Support

For issues or questions:
- **GitHub Issues**: [Report a bug](https://github.com/Psqasim/hackathon-todo/issues)
- **Hugging Face**: [HF Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- **Vercel**: [Vercel Documentation](https://vercel.com/docs)
- **Neon**: [Neon Documentation](https://neon.tech/docs)

---

**Last Updated**: 2026-02-02
**Author**: [Muhammad Qasim](https://github.com/Psqasim)
**License**: MIT

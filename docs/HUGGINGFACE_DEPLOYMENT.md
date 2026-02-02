# Hugging Face Spaces Deployment Guide

## Research Summary

This guide documents the preparation of the TaskFlow backend for deployment to Hugging Face Spaces.

### Key Research Insights

#### 1. Port Configuration
- **Port 7860**: Hugging Face Spaces expose applications on port 7860 (required)
- **Internal Ports**: Can run multiple services internally (8000 for FastAPI, 8001 for MCP server)
- **External Access**: Only port 7860 is exposed to the internet
- Configuration via `app_port: 7860` in README.md YAML block

#### 2. Docker SDK Requirements
- README.md must have YAML frontmatter at the top
- Required fields: `title`, `emoji`, `colorFrom`, `colorTo`, `sdk: docker`, `app_port`
- Sets up automatic Docker container deployment

#### 3. Multiple Services Architecture
- FastAPI backend runs on internal port 8000
- MCP server runs on internal port 8001
- Port 7860 proxies to FastAPI (main entry point)
- Both services start via shell command in CMD

#### 4. Filesystem Restrictions
- **Write Access**: Only `/tmp` directory is writable
- **Model Caches**: Must redirect to `/tmp` (Transformers, PyTorch, etc.)
- **Logs**: Store in `/tmp/logs`

#### 5. Best Practices
- Use Python 3.12+ base image
- Install UV package manager for dependency management
- Include health check endpoint
- Use multi-stage builds if needed for size optimization
- Handle graceful shutdown for both services

## Files Created

### 1. Dockerfile
**Location**: `/Dockerfile`

**Purpose**: Container configuration for Hugging Face Spaces

**Key Features**:
- Python 3.12 slim base image
- UV package manager installation
- Installs all backend dependencies from pyproject.toml
- Copies backend source code (src/ directory)
- Exposes port 7860
- Health check on `/health` endpoint
- Starts both FastAPI (port 7860) and MCP server (port 8001)

**Multi-Service Start Command**:
```bash
uv run python -m src.mcp_server.server & \
uv run uvicorn src.interfaces.api:app --host 0.0.0.0 --port 7860 --workers 1
```

### 2. requirements.txt
**Location**: `/requirements.txt`

**Purpose**: Python dependencies for Hugging Face deployment

**Dependencies Included**:
- **Web Framework**: fastapi, uvicorn
- **Database**: sqlmodel, psycopg2-binary
- **Authentication**: python-jose, bcrypt, passlib
- **Data Validation**: pydantic, pydantic-settings
- **HTTP Client**: httpx
- **AI Integration**: fastmcp, openai, openai-agents, dateparser
- **Utilities**: python-dotenv, structlog, rich

**Total**: 20+ production dependencies

### 3. README.md Update
**Change**: Added Hugging Face YAML frontmatter

**Configuration**:
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

## Project Structure Analysis

### Backend Components
```
src/
├── interfaces/
│   └── api.py              # FastAPI app (1484 lines)
├── mcp_server/
│   ├── server.py           # MCP server entry (120 lines)
│   ├── agent.py            # TaskAgent with OpenAI integration
│   ├── tools.py            # 8 MCP tools for task management
│   ├── backend_client.py   # HTTP client for FastAPI
│   ├── auth.py             # Authentication helpers
│   ├── memory.py           # Conversation memory
│   ├── nlp.py              # NLP utilities
│   └── prompts.py          # System prompts
├── agents/                 # Multi-agent architecture
├── backends/               # Storage backends
├── models/                 # Data models
├── auth/                   # JWT & password handling
├── config.py              # Environment settings
└── db.py                  # Database connection
```

### Environment Variables Required

**Critical**:
- `DATABASE_URL`: PostgreSQL connection (Neon)
- `JWT_SECRET_KEY`: 32-char secret for JWT tokens
- `OPENAI_API_KEY`: OpenAI API key for chat (Phase III)

**Optional**:
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`: Google OAuth
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`: GitHub OAuth
- `FRONTEND_URL`: Frontend deployment URL
- `BACKEND_URL`: Backend deployment URL

**MCP Server**:
- `MCP_SERVER_PORT`: 8001 (default)
- `MCP_BACKEND_URL`: Internal FastAPI URL

## Deployment Steps

### 1. Create Hugging Face Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Fill in details:
   - **Space name**: taskflow-backend
   - **License**: MIT
   - **SDK**: Docker
   - **Visibility**: Public or Private
4. Click "Create Space"

### 2. Push Code to Hugging Face

```bash
# Initialize git (if not already done)
git init

# Add Hugging Face remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/taskflow-backend

# Commit deployment files
git add Dockerfile requirements.txt README.md
git commit -m "feat: Add Hugging Face Spaces deployment configuration"

# Push to Hugging Face
git push hf main
```

### 3. Configure Environment Variables

In Hugging Face Space Settings:

1. Go to **Settings** → **Repository secrets**
2. Add the following secrets:
   - `DATABASE_URL`: Your Neon PostgreSQL URL
   - `JWT_SECRET_KEY`: Generate with `openssl rand -hex 32`
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `FRONTEND_URL`: Your Vercel frontend URL
   - `BACKEND_URL`: https://YOUR_USERNAME-taskflow-backend.hf.space
   - (Optional) OAuth credentials

### 4. Wait for Build

- Hugging Face will automatically build the Docker image
- Build logs available in the "Logs" tab
- First build takes 5-10 minutes
- Subsequent builds are faster (cached layers)

### 5. Test Deployment

Once deployed, test these endpoints:

```bash
# Health check
curl https://YOUR_USERNAME-taskflow-backend.hf.space/health

# Database health
curl https://YOUR_USERNAME-taskflow-backend.hf.space/api/health/db

# API documentation
curl https://YOUR_USERNAME-taskflow-backend.hf.space/docs
```

## Architecture Differences

### Local Development (3 Services)
```
Terminal 1: FastAPI (port 8000)
Terminal 2: MCP Server (port 8001)
Terminal 3: Next.js Frontend (port 3000)
```

### Hugging Face Deployment (1 Container)
```
Docker Container:
├── FastAPI (internal: port 7860, external: port 7860)
└── MCP Server (internal: port 8001, not exposed)
```

**Frontend**: Still deployed separately on Vercel, connects to HF backend

## Service Communication

### Internal (Within Container)
- MCP Server → FastAPI: `http://localhost:7860` or `http://127.0.0.1:7860`
- Agent calls backend via BackendClient using internal URL

### External (From Frontend)
- Frontend → FastAPI: `https://YOUR_USERNAME-taskflow-backend.hf.space`
- All REST API calls go through port 7860

## Limitations & Considerations

### Hugging Face Spaces Constraints
1. **Compute**: Free tier has CPU limits
2. **Memory**: 16GB RAM limit (free tier)
3. **Storage**: Ephemeral (resets on restart)
4. **Write Access**: Only `/tmp` directory
5. **Networking**: Only port 7860 exposed

### Database Recommendation
- Use **Neon PostgreSQL** (managed, external)
- Don't store data in container (ephemeral)
- Already configured in project

### MCP Server Consideration
- Runs on internal port 8001
- Not accessible from outside
- Only FastAPI backend can call it
- Consider separate deployment if needed externally

## Cost Estimation

### Free Tier
- **Hugging Face**: Free (CPU, limited resources)
- **Neon PostgreSQL**: Free tier (0.5GB storage)
- **Vercel Frontend**: Free tier (100GB bandwidth)
- **OpenAI API**: Pay-per-use (~$0.15 per 1M tokens for gpt-4o-mini)

### Paid Tier (Optional)
- **Hugging Face Pro**: $9/month (better hardware)
- **Neon Scale**: $19/month (1GB storage, better performance)
- **Vercel Pro**: $20/month (unlimited bandwidth)

## Monitoring & Debugging

### Health Checks
- **FastAPI Health**: `/health` endpoint
- **Database Health**: `/api/health/db` endpoint
- **MCP Server Health**: Check logs for startup message

### Logs Access
- Hugging Face Spaces → **Logs** tab
- Real-time log streaming
- Check for errors during startup

### Common Issues

**Issue**: Port binding error
**Solution**: Ensure FastAPI runs on 0.0.0.0:7860, not 127.0.0.1

**Issue**: MCP server not starting
**Solution**: Check OPENAI_API_KEY is set in secrets

**Issue**: Database connection failed
**Solution**: Verify DATABASE_URL includes `?sslmode=require`

**Issue**: 404 errors
**Solution**: Check CORS settings in api.py allow HF domain

## Next Steps

After successful deployment:

1. **Update Frontend**: Point `NEXT_PUBLIC_API_URL` to Hugging Face Space URL
2. **Test OAuth**: Update OAuth redirect URIs in Google/GitHub
3. **Monitor Performance**: Check response times and error rates
4. **Scale if Needed**: Upgrade to Hugging Face Pro if hitting limits
5. **Set Up CI/CD**: Automate deployments on git push

## Resources

### Official Documentation
- [Docker Spaces](https://huggingface.co/docs/hub/en/spaces-sdks-docker)
- [Spaces Configuration Reference](https://huggingface.co/docs/hub/en/spaces-config-reference)
- [Docker Spaces First Demo](https://huggingface.co/docs/hub/en/spaces-sdks-docker-first-demo)

### Community Resources
- [Deploying FastAPI on Huggingface Via Docker](https://huggingface.co/blog/HemanthSai7/deploy-applications-on-huggingface-spaces)
- [Handling HF Restrictions](https://medium.com/@na.mazaheri/deploying-a-fastapi-app-on-hugging-face-spaces-and-handling-all-its-restrictions-d494d97a78fa)
- [Building AI-Powered APIs with FastAPI and OpenAI Agents SDK](https://blog.devgenius.io/building-ai-powered-apis-with-fastapi-and-openai-agents-sdk-deployment-on-hugging-face-2ce34d3eb766)

### Technical References
- [Build ML Apps with HF Docker Spaces](https://www.docker.com/blog/build-machine-learning-apps-with-hugging-faces-docker-spaces/)
- [Port Binding Issue Discussion](https://discuss.huggingface.co/t/port-binding-issue-uvicorn-app-running-but-space-shows-404-docker-fastapi/170027)

## Support

For issues or questions:
- **GitHub**: [Open an issue](https://github.com/Psqasim/hackathon-todo/issues)
- **Hugging Face**: Check community forums
- **Author**: [Muhammad Qasim](https://github.com/Psqasim)

---

**Last Updated**: 2026-02-02
**Status**: Ready for deployment
**Next Phase**: Deploy to Hugging Face Spaces

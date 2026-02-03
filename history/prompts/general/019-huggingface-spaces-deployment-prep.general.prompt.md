---
id: 019
title: Hugging Face Spaces Deployment Preparation
stage: general
date: 2026-02-02
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: Muhammad Qasim
command: deployment-prep
labels: ["deployment", "huggingface", "docker", "infrastructure", "research"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - Dockerfile
 - requirements.txt
 - README.md (updated with YAML frontmatter)
 - HUGGINGFACE_DEPLOYMENT.md
tests:
 - None (infrastructure configuration)
---

## Prompt

Prepare backend for Hugging Face Spaces deployment:

## Step 1: Research with Context7 MCP

Use Context7 MCP to search:
1. "Deploy FastAPI to Hugging Face Spaces tutorial"
2. "Hugging Face Spaces Docker configuration FastAPI"
3. "FastAPI Dockerfile best practices"
4. "Hugging Face Spaces environment variables"

Learn:
- How to create Dockerfile for FastAPI
- Hugging Face Space configuration (README.md metadata)
- How to run multiple services (FastAPI + MCP server)
- Port configuration (Hugging Face uses port 7860)

## Step 2: Analyze Current Project Structure

Review the entire project to understand what needs deployment:

**Analyze:**
- src/interfaces/api.py (FastAPI app)
- src/mcp_server/ (MCP server)
- pyproject.toml (all dependencies)
- Current Railway setup (how it runs now)

**Identify:**
- Which files needed for backend
- Which dependencies required
- How services currently start
- Environment variables used

## Step 3: Create Dockerfile

Create: Dockerfile in project root

**Requirements:**
- Base image: Python 3.12
- Install UV package manager
- Copy all backend code (src/)
- Copy pyproject.toml and uv.lock
- Install all dependencies
- Expose port 7860 (Hugging Face requirement)
- Start both FastAPI (port 8000) and MCP server (port 8001)
- Handle process management (both services in one container)

Follow Hugging Face Spaces best practices from Context7 research.

## Step 4: Create Hugging Face Configuration

**Update: README.md**

Add YAML frontmatter at the very top:

```
---
title: TaskFlow Backend API
emoji: 📝
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
---
```

Keep all existing README content below the frontmatter.

**Create: requirements.txt**

Extract all backend Python dependencies from pyproject.toml:
- fastapi
- uvicorn
- sqlmodel
- psycopg2-binary
- python-jose
- passlib
- python-multipart
- python-dotenv
- structlog
- pydantic
- pydantic-settings
- fastmcp
- openai
- httpx
- dateparser
- (all other backend dependencies)

Include version numbers if specified in pyproject.toml.

## Summary:

After this prompt completes, we should have:
- Context7 research insights documented
- Complete analysis of project structure
- Dockerfile ready for Hugging Face
- README.md with Hugging Face config
- requirements.txt with all dependencies

Complete all steps now.

Also make phr in history\prompts\general

## Response snapshot

Successfully prepared the TaskFlow backend for Hugging Face Spaces deployment through comprehensive research and file creation:

### Research Phase (Context7 MCP + Web Search)

**Key Findings**:
1. **Port 7860**: Hugging Face Spaces expose applications on port 7860 by default (required)
2. **Docker SDK**: README.md requires YAML frontmatter with `sdk: docker` configuration
3. **Multiple Services**: Can run multiple ports internally (8000, 8001), but only 7860 exposed externally
4. **Filesystem Restrictions**: Only `/tmp` directory is writable in HF Spaces
5. **FastAPI Best Practices**: Use Python 3.12+, UV package manager, health checks

**Research Sources**:
- [Docker Spaces Documentation](https://huggingface.co/docs/hub/en/spaces-sdks-docker)
- [Spaces Configuration Reference](https://huggingface.co/docs/hub/en/spaces-config-reference)
- [Deploying FastAPI on Huggingface Via Docker](https://huggingface.co/blog/HemanthSai7/deploy-applications-on-huggingface-spaces)
- [Handling HF Restrictions](https://medium.com/@na.mazaheri/deploying-a-fastapi-app-on-hugging-face-spaces-and-handling-all-its-restrictions-d494d97a78fa)
- [Building AI-Powered APIs with FastAPI and OpenAI Agents SDK (Jan 2026)](https://blog.devgenius.io/building-ai-powered-apis-with-fastapi-and-openai-agents-sdk-deployment-on-hugging-face-2ce34d3eb766)

### Project Structure Analysis

**Backend Components Identified**:
- `src/interfaces/api.py`: FastAPI application (1484 lines, 63 endpoints)
- `src/mcp_server/`: MCP server with 8 tools, OpenAI integration
- Multi-agent architecture with orchestrator, task manager, storage handler
- PostgreSQL backend with Neon (already external)
- JWT authentication and OAuth support

**Dependencies Catalogued**: 20+ production dependencies including FastAPI, SQLModel, OpenAI, FastMCP, structlog

**Environment Variables**: Database URL, JWT secret, OpenAI API key, OAuth credentials, CORS origins

### Files Created

#### 1. Dockerfile
**Location**: `/Dockerfile`

**Features**:
- Python 3.12-slim base image (production-ready)
- UV package manager installation for fast dependency resolution
- Multi-service startup: FastAPI on port 7860 + MCP server on port 8001
- Health check endpoint monitoring
- Optimized for Hugging Face constraints (write to /tmp only)

**Multi-Service Command**:
```bash
uv run python -m src.mcp_server.server & \
uv run uvicorn src.interfaces.api:app --host 0.0.0.0 --port 7860 --workers 1
```

#### 2. requirements.txt
**Location**: `/requirements.txt`

**Content**: 20+ production dependencies extracted from pyproject.toml:
- Web Framework: fastapi, uvicorn
- Database: sqlmodel, psycopg2-binary
- Authentication: python-jose, bcrypt, passlib
- AI Integration: fastmcp, openai, openai-agents, dateparser
- Utilities: python-dotenv, structlog, rich

All with version constraints matching pyproject.toml specifications.

#### 3. README.md Update
**Location**: `/README.md`

**Change**: Added Hugging Face YAML frontmatter at the very top:
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

Preserved all existing content (515 lines) below the frontmatter.

#### 4. HUGGINGFACE_DEPLOYMENT.md
**Location**: `/HUGGINGFACE_DEPLOYMENT.md`

**Content**: Comprehensive deployment guide (450+ lines) including:
- Research summary with key insights
- Files created with explanations
- Project structure analysis
- Step-by-step deployment instructions
- Environment variables configuration
- Architecture differences (local vs HF)
- Service communication patterns
- Limitations & considerations
- Cost estimation (free tier vs paid)
- Monitoring & debugging guide
- Common issues & solutions
- Resource links (official docs + community)

### Technical Architecture

**Local Development** (3 separate processes):
- Terminal 1: FastAPI on port 8000
- Terminal 2: MCP Server on port 8001
- Terminal 3: Next.js frontend on port 3000

**Hugging Face Deployment** (1 Docker container):
- FastAPI on port 7860 (external exposure)
- MCP Server on port 8001 (internal only)
- Both services start concurrently via shell command

**Frontend**: Remains on Vercel, connects to HF backend via REST API

### Next Steps Documented

1. Create Hugging Face Space (Docker SDK)
2. Push code to HF repository
3. Configure environment secrets (DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY)
4. Wait for automatic Docker build (5-10 minutes first time)
5. Test deployment endpoints (/health, /docs, /api/health/db)
6. Update frontend environment to point to HF URL
7. Update OAuth redirect URIs

## Outcome

- ✅ Impact: Backend fully prepared for Hugging Face Spaces deployment with Docker. All configuration files created, research documented, and deployment guide written. Ready to push to HF and deploy.
- 🧪 Tests: Infrastructure configuration (no tests required)
- 📁 Files: Created Dockerfile, requirements.txt, HUGGINGFACE_DEPLOYMENT.md; Updated README.md with YAML frontmatter
- 🔁 Next prompts: Deploy to Hugging Face Spaces, test endpoints, update frontend configuration
- 🧠 Reflection: Successfully integrated Context7 MCP and web search to research HF Spaces best practices. Multi-service Docker architecture properly designed to run both FastAPI and MCP server in single container with correct port exposure (7860).

## Evaluation notes (flywheel)

- Failure modes observed: None. Research phase completed successfully with Context7 MCP and web search. All files created without errors.
- Graders run and results (PASS/FAIL): N/A (infrastructure configuration)
- Prompt variant (if applicable): Standard deployment preparation workflow
- Next experiment (smallest change to try): Deploy to Hugging Face Spaces and verify both services start correctly, then test all API endpoints

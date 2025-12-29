---
id: 015
title: Railway Deployment Configuration
stage: general
date: 2025-12-29
surface: agent
model: claude-opus-4-5-20251101
feature: 002-fullstack-web-app
branch: main
user: psqasim
command: conversation
labels: ["railway", "deployment", "cors", "config", "production"]
links:
  spec: specs/002-fullstack-web-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - railway.json
  - Procfile
  - runtime.txt
  - src/config.py
  - src/interfaces/api.py
tests:
  - Railway deployment build
---

## Prompt

Prepare the backend for Railway deployment:
1. Create Railway-specific files (railway.json, Procfile, runtime.txt)
2. Update src/config.py to handle Railway environment
3. Update src/interfaces/api.py CORS settings
4. Push to GitHub
5. Create PHR

## Response snapshot

### Files Created:

**1. railway.json**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn src.interfaces.api:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**2. Procfile**
```
web: uvicorn src.interfaces.api:app --host 0.0.0.0 --port $PORT
```

**3. runtime.txt**
```
python-3.12
```

### Config Updates (src/config.py):

**Railway Detection:**
```python
IS_RAILWAY = os.getenv("RAILWAY_ENVIRONMENT") is not None
RAILWAY_PUBLIC_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN", "")
```

**Dynamic URL Functions:**
- `get_frontend_url()` - Returns Vercel URL on Railway, localhost otherwise
- `get_backend_url()` - Uses RAILWAY_PUBLIC_DOMAIN on Railway
- `get_allowed_origins()` - Computes CORS origins based on environment

**ALLOWED_ORIGINS Export:**
```python
ALLOWED_ORIGINS = get_allowed_origins()
```

### API Updates (src/interfaces/api.py):

**Import change:**
```python
from src.config import ALLOWED_ORIGINS, settings
```

**CORS middleware:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Dynamic instead of hardcoded
    ...
)
```

### Pushed to GitHub:
- Commit: e2d7182
- 5 files changed, 61 insertions(+), 9 deletions(-)

## Outcome

- Impact: Backend ready for Railway deployment with proper environment detection
- Tests: Awaiting Railway deployment
- Files: 5 files created/modified
- Next prompts: Deploy to Railway, configure environment variables
- Reflection: Environment-aware configuration essential for cloud deployments

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Pending Railway deployment
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add health check endpoint for Railway monitoring

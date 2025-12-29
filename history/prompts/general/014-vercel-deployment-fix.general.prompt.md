---
id: 014
title: Vercel Deployment Missing Lib Fix
stage: general
date: 2025-12-29
surface: agent
model: claude-opus-4-5-20251101
feature: 002-fullstack-web-app
branch: main
user: psqasim
command: conversation
labels: ["vercel", "deployment", "gitignore", "build-error", "fix"]
links:
  spec: specs/002-fullstack-web-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .gitignore
  - frontend/lib/auth-client.ts
  - frontend/lib/api-client.ts
tests:
  - Vercel deployment build
---

## Prompt

When deploying to Vercel, build failed with 7 errors:
- Module not found: Can't resolve '@/lib/api-client'
- Module not found: Can't resolve '@/lib/auth-client'

Fix this and push the code to GitHub.

## Response snapshot

### Root Cause:
The `frontend/lib/` folder was excluded from git by the root `.gitignore` file which had:
```
lib/
```

This pattern was intended to ignore Python's lib directory but was also matching `frontend/lib/`.

### Fix Applied:

**1. Updated .gitignore:**
```gitignore
lib/
!frontend/lib/    # <-- Added exception
lib64/
```

**2. Added missing files to git:**
- `frontend/lib/auth-client.ts` - JWT auth helpers (signout, signin, signup, etc.)
- `frontend/lib/api-client.ts` - API client with auth headers (getTasks, createTask, etc.)

**3. Committed and pushed:**
```
fix: add missing frontend/lib files for Vercel deployment

- Added frontend/lib/auth-client.ts (JWT auth helpers)
- Added frontend/lib/api-client.ts (API client with auth)
- Updated .gitignore to not ignore frontend/lib/
```

### Files Added:
- `frontend/lib/auth-client.ts` - 4,746 bytes
- `frontend/lib/api-client.ts` - 5,052 bytes

## Outcome

- Impact: Vercel deployment should now succeed with lib files included
- Tests: Awaiting Vercel rebuild
- Files: 3 files modified/added
- Next prompts: Verify Vercel deployment succeeds
- Reflection: Python gitignore patterns can accidentally exclude frontend directories

## Evaluation notes (flywheel)

- Failure modes observed: Generic gitignore patterns (lib/) affecting unexpected directories
- Graders run and results (PASS/FAIL): Pending Vercel rebuild
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Use more specific patterns like /lib/ (root only) instead of lib/

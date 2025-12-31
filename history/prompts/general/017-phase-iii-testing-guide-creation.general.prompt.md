---
id: "017"
title: Phase III Testing Guide Creation
stage: general
date: 2025-12-30
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 002-fullstack-web-app
user: developer
command: manual request
labels: ["documentation", "testing", "phase-iii", "setup-guide"]
links:
  spec: specs/003-ai-chatbot-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - docs/PHASE-III-TESTING-GUIDE.md
tests:
  - N/A (documentation only)
---

## Prompt

Create comprehensive testing and setup guide for Phase III AI Chatbot:

## Part 1: Environment Setup
- Backend .env file requirements with OPENAI_API_KEY
- Frontend .env.local file requirements

## Part 2: How to Run Phase III
- 3 terminal setup (Backend API, MCP Server, Frontend)
- Expected outputs for each service

## Part 3: Manual Testing Steps
- 10 detailed test scenarios with expected behaviors

## Part 4: Automated Tests
- Backend pytest commands
- Frontend test commands

## Part 5: Verify All Phases Still Work
- Phase I console verification
- Phase II web UI verification
- Phase III chat verification

## Part 6: Common Issues & Fixes
- 7 common issues with solutions

## Part 7: Cost Monitoring
- OpenAI API pricing and usage estimates

## Part 8: Production Deployment Checklist
- Railway backend checklist
- Vercel frontend checklist

## Response snapshot

Created comprehensive testing guide at `docs/PHASE-III-TESTING-GUIDE.md` with:

### Part 1: Environment Setup
- Complete .env variables for backend (OPENAI_API_KEY, MCP_SERVER_PORT, MCP_BACKEND_URL)
- Frontend .env.local variables
- Environment verification commands

### Part 2: How to Run Phase III
- Terminal 1: `uv run uvicorn src.interfaces.api:app --reload --port 8000`
- Terminal 2: `uv run python -m src.mcp_server.server`
- Terminal 3: `cd frontend && npm run dev`
- Expected outputs and health check commands

### Part 3: Manual Testing Steps (10 tests)
1. Check MCP Server Health
2. Access Chat UI
3. Send First Message
4. Create Task via Natural Language
5. Verify Task in Phase II Dashboard
6. Context Awareness Test
7. Mobile Responsiveness
8. Search and Filter via Chat
9. Task Completion via Chat
10. Delete Task via Chat

### Part 4: Automated Tests
- `uv run pytest tests/ -v --cov=src`
- Frontend test commands
- Expected coverage output

### Part 5: Cross-Phase Verification
- Phase I console: `uv run todo`
- Phase II dashboard tests
- Phase III chat integration tests

### Part 6: Common Issues & Fixes
1. OpenAI API key not found
2. MCP Server won't start (port conflict)
3. Chat UI connection error
4. Agent doesn't call tools
5. CORS errors
6. Database connection failed
7. Conversation history not loading

### Part 7: Cost Monitoring
- gpt-4o-mini pricing: $0.15/1M input, $0.60/1M output tokens
- $7 credit ≈ 5,000-10,000 chat messages
- Usage monitoring URL

### Part 8: Production Deployment Checklist
- Railway: Environment variables, health endpoints, 8 MCP tools
- Vercel: Environment variables, build verification, OAuth callbacks
- Post-deployment verification steps

### Part 9: Quick Reference Commands
- All startup commands in one place
- Health check commands
- Log viewing commands

## Outcome

- ✅ Impact: Comprehensive 500+ line testing guide for Phase III AI Chatbot
- 🧪 Tests: Documents 10 manual test scenarios + automated test commands
- 📁 Files: 1 file created (docs/PHASE-III-TESTING-GUIDE.md)
- 🔁 Next prompts: Run through all manual tests, deploy to production
- 🧠 Reflection: Guide covers all aspects from setup to deployment, making Phase III reproducible for any developer

## Evaluation notes (flywheel)

- Failure modes observed: None - documentation task
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add video walkthrough or GIF demonstrations for visual learners

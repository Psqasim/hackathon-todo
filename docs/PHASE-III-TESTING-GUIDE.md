# Phase III: AI Chatbot Testing & Setup Guide

Comprehensive guide for setting up, running, and testing the AI Chatbot with MCP Integration.

---

## Part 1: Environment Setup

### Backend .env File (Root Directory)

Add these variables to your root `.env` file:

```bash
# =============================================================================
# Existing Phase II Variables (keep these)
# =============================================================================
DATABASE_URL=postgresql://user:password@host:5432/dbname
JWT_SECRET_KEY=your-secret-key-here
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth (optional)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# =============================================================================
# NEW - Phase III Variables
# =============================================================================
# OpenAI API Key (REQUIRED for chat functionality)
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# MCP Server Configuration
MCP_SERVER_PORT=8001
MCP_BACKEND_URL=http://localhost:8000
```

### Frontend .env.local File (frontend/.env.local)

```bash
# =============================================================================
# Existing Phase II Variables (keep these)
# =============================================================================
NEXT_PUBLIC_API_URL=http://localhost:8000

# =============================================================================
# NEW - Phase III Variables
# =============================================================================
# Enable chat feature (optional, defaults to true)
NEXT_PUBLIC_CHAT_ENABLED=true
```

### Verify Environment Files

```bash
# Check backend .env exists
cat .env | grep OPENAI_API_KEY

# Check frontend .env.local exists
cat frontend/.env.local | grep NEXT_PUBLIC_API_URL
```

---

## Part 2: How to Run Phase III

### Prerequisites

1. **Python 3.12+** with uv package manager
2. **Node.js 20+** with npm
3. **PostgreSQL** database running
4. **OpenAI API Key** with credit ($7 minimum recommended)

### Terminal Setup (3 Terminals Needed)

Open 3 terminal windows/tabs:

---

#### Terminal 1 - Backend API (Port 8000)

```bash
cd /mnt/d/gov\ ai\ code/QUATER\ 4\ part\ 2/hacakthon/hackathon-todo

# Run FastAPI backend
uv run uvicorn src.interfaces.api:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     database_engine_created database_url=postgresql://user@***
INFO:     database_tables_created
INFO:     api_starting
INFO:     Application startup complete.
```

**Verify:** Open http://localhost:8000/health - should return `{"status": "healthy"}`

---

#### Terminal 2 - MCP Server (Port 8001)

```bash
cd /mnt/d/gov\ ai\ code/QUATER\ 4\ part\ 2/hacakthon/hackathon-todo

# Run MCP Server
uv run python -m src.mcp_server.server
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started server process [12347]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify:** Open http://localhost:8001/health - should return JSON with status

---

#### Terminal 3 - Frontend (Port 3000)

```bash
cd /mnt/d/gov\ ai\ code/QUATER\ 4\ part\ 2/hacakthon/hackathon-todo/frontend

# Install dependencies (if first time)
npm install

# Run Next.js development server
npm run dev
```

**Expected output:**
```
   ▲ Next.js 16.1.1
   - Local:        http://localhost:3000
   - Environments: .env.local

 ✓ Starting...
 ✓ Ready in 2.3s
```

**Verify:** Open http://localhost:3000 - should show TaskFlow homepage

---

## Part 3: Manual Testing Steps

### Test 1: Check MCP Server Health

```bash
curl http://localhost:8001/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "openai_configured": true,
  "backend_reachable": true,
  "mcp_server_port": 8001,
  "backend_url": "http://localhost:8000"
}
```

**If `openai_configured: false`:** Check OPENAI_API_KEY in .env file

---

### Test 2: Privacy Notice Modal

1. Open browser: http://localhost:3000
2. Sign in with existing Phase II account (or create new one)
3. Click **"AI Chat"** in the navigation header
4. **First time only:** Privacy notice modal should appear

**Expected privacy notice content:**
- Header: "Privacy Notice"
- Explains data handling:
  - Tasks stored in your database
  - Chat history stored with OpenAI for 30 days
  - Data not used for training
- Two buttons:
  - "Go to Dashboard" - redirects away
  - "I Agree & Continue" - saves consent, shows chat

**Test privacy decline:**
1. Click "Go to Dashboard"
2. Should redirect to /dashboard
3. Return to /chat - modal shows again

**Test privacy accept:**
1. Click "I Agree & Continue"
2. Modal closes
3. Chat interface appears
4. Refresh page - modal should NOT appear again

**Verify consent storage:**
```javascript
// In browser console
localStorage.getItem('taskflow_chat_privacy_consent')
// Should return: "true"
```

**Reset consent for testing:**
```javascript
localStorage.removeItem('taskflow_chat_privacy_consent')
```

---

### Test 3: Access Chat UI (After Consent)

1. After accepting privacy notice
2. Should see chat interface with:
   - Purple AI avatar icon
   - "Task Assistant" title
   - Welcome message with your name
   - Quick action buttons
   - Input box at bottom

**Screenshot checkpoint:** Chat welcome screen visible

---

### Test 4: Send First Message

In the chat UI, type:
```
Show me all my tasks
```

**Expected behavior:**
1. Your message appears in blue bubble (right side)
2. Typing indicator (3 animated dots) appears
3. Agent responds with list of your tasks
4. Response appears in white bubble (left side)
5. Tool call indicator shows "1 action performed"

**If no tasks exist:** Agent will say "You don't have any tasks yet. Would you like to create one?"

---

### Test 5: Create Task via Natural Language

In chat UI, type:
```
Add a task to buy groceries tomorrow with high priority
```

**Expected behavior:**
1. Agent extracts:
   - title: "buy groceries"
   - due_date: tomorrow's date (ISO format)
   - priority: "high"
2. Agent calls `add_task` tool
3. Confirmation message: "I've created the task 'buy groceries' for tomorrow with high priority."

**Verify in database:**
```bash
# Check task was created
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/users/YOUR_USER_ID/tasks
```

---

### Test 6: Verify Task in Phase II Dashboard

1. Navigate to: http://localhost:3000/dashboard
2. Look for "buy groceries" task
3. Verify:
   - Title: "buy groceries"
   - Priority: High (should show orange/red indicator)
   - Due date: Tomorrow's date
4. Try completing the task via checkbox
5. Go back to chat and ask "Show my completed tasks"

**Integration verified:** Tasks created in chat appear in dashboard

---

### Test 7: Context Awareness Test (OpenAI Conversations API)

**Architecture Note:** Conversation history is stored in OpenAI's Conversations API, NOT locally. Each conversation has a unique `conversation_id` managed by OpenAI.

In chat UI, send these messages **in sequence**:

```
Message 1: Add a task to call mom
```
Wait for response, then:
```
Message 2: Change that to urgent priority
```

**Expected behavior:**
1. First message creates task "call mom" with default priority
2. Second message:
   - Agent understands "that" refers to "call mom" (context from OpenAI session)
   - Calls `update_task` with last_task_id from context
   - Confirms: "I've updated the task 'call mom' to urgent priority."

**Context features verified:**
- OpenAI Conversations API maintains message history
- Pronoun resolution ("that", "it") via session memory
- Follow-up question handling
- `conversation_id` persisted in frontend localStorage

**How to verify stateless backend:**
1. Check browser localStorage: `localStorage.getItem('taskflow_conversations')`
2. Should see: `[{"id": "conv_xxx", "title": "...", ...}]`
3. Messages are NOT in localStorage - only `id`, `title`, timestamps
4. PostgreSQL has NO `conversations` or `messages` tables

---

### Test 8: Mobile Responsiveness

1. Open Chrome DevTools: Press F12 (or Cmd+Option+I on Mac)
2. Toggle device toolbar: Click phone icon or press Ctrl+Shift+M
3. Select device: "iPhone SE" (320px width)

**Verify:**
- [ ] Chat bubbles fit within screen width
- [ ] Text doesn't overflow
- [ ] Input box stays at bottom
- [ ] Send button is easily tappable (44x44px minimum)
- [ ] Scrolling through messages works smoothly
- [ ] Quick action buttons wrap correctly
- [ ] Header navigation collapses appropriately

**Test landscape mode:**
1. Rotate device in DevTools
2. Chat should remain usable

---

### Test 9: Search and Filter via Chat

Test natural language search:
```
Find tasks with the word "groceries"
```

**Expected:** Agent calls `search_tasks` and returns matching tasks

Test filtering:
```
Show me all urgent tasks
```

**Expected:** Agent calls `filter_tasks` with priority="urgent"

Test date filtering:
```
What tasks are due this week?
```

**Expected:** Agent calculates date range and calls `filter_tasks`

---

### Test 10: Task Completion via Chat

```
Mark the groceries task as complete
```

**Expected:**
- Agent calls `complete_task` tool
- Confirms completion
- Task status changes to "completed"

Verify reversal:
```
Actually, mark it as not complete
```

**Expected:** Task reverts to "pending" status

---

### Test 11: Delete Task via Chat

```
Delete the groceries task
```

**Expected:**
- Agent may ask for confirmation (depends on prompt)
- Calls `delete_task` tool
- Confirms deletion
- Task no longer appears in list

---

## Part 4: Automated Tests

### Run All Backend Tests

```bash
cd /mnt/d/gov\ ai\ code/QUATER\ 4\ part\ 2/hacakthon/hackathon-todo

# Run all tests with coverage
uv run pytest tests/ -v --cov=src --cov-report=term-missing
```

**Expected output:**
```
tests/unit/test_nlp.py::test_parse_natural_date_today PASSED
tests/unit/test_nlp.py::test_parse_natural_date_tomorrow PASSED
... (35 NLP tests)

---------- coverage: platform linux ---------
Name                              Stmts   Miss  Cover
-----------------------------------------------------
src/mcp_server/nlp.py               45      2    96%
src/mcp_server/agent.py            180     30    83%
src/mcp_server/memory.py            95     15    84%
...
-----------------------------------------------------
TOTAL                              850    150    82%

35 passed in 5.23s
```

### Run Specific Test Suites

```bash
# NLP tests only
uv run pytest tests/unit/test_nlp.py -v

# Agent tests only (if created)
uv run pytest tests/unit/test_agent.py -v

# Integration tests
uv run pytest tests/integration/ -v
```

### Run Frontend Tests

```bash
cd /mnt/d/gov\ ai\ code/QUATER\ 4\ part\ 2/hacakthon/hackathon-todo/frontend

# Run Jest tests (if configured)
npm test

# Run with coverage
npm test -- --coverage
```

---

## Part 5: Verify All Phases Still Work

### Phase I: Console Application

```bash
cd /mnt/d/gov\ ai\ code/QUATER\ 4\ part\ 2/hacakthon/hackathon-todo

# Run console interface
uv run todo
```

**Expected:** Rich console menu appears with:
1. Add Task
2. List Tasks
3. Complete Task
4. Delete Task
5. Exit

**Test:** Create a task, verify it appears in both Phase II and Phase III

---

### Phase II: Web Dashboard

1. Navigate to: http://localhost:3000
2. Sign in with email/password
3. Test all CRUD operations:
   - [ ] Create new task
   - [ ] Edit existing task
   - [ ] Mark task complete
   - [ ] Delete task
   - [ ] Filter by status
   - [ ] Sort by priority

4. Test OAuth (if configured):
   - [ ] Sign in with Google
   - [ ] Sign in with GitHub

---

### Phase III: AI Chat

1. Navigate to: http://localhost:3000/chat
2. Chat with AI assistant
3. Tasks created via chat appear in Phase II dashboard
4. Tasks from Phase II can be managed via chat

**Cross-phase verification:**
```
1. Create task in Phase I console
2. Verify appears in Phase II dashboard
3. Modify via Phase III chat
4. Verify changes in Phase II
```

---

## Part 6: Common Issues & Fixes

### Issue 1: "OpenAI API key not found"

**Symptoms:**
- Chat returns "Chat processing failed"
- MCP health shows `openai_configured: false`

**Fix:**
```bash
# Add to .env file
echo 'OPENAI_API_KEY=sk-proj-your-key-here' >> .env

# Restart backend and MCP server
```

---

### Issue 2: MCP Server Won't Start

**Symptoms:**
- "Address already in use" error
- Port 8001 conflict

**Fix:**
```bash
# Kill process using port 8001
lsof -ti:8001 | xargs kill -9

# Or use different port
MCP_SERVER_PORT=8002 uv run python -m src.mcp_server.server
```

---

### Issue 3: Chat UI Shows Connection Error

**Symptoms:**
- "Failed to send message"
- Network error in console

**Fix:**
1. Verify MCP server is running: `curl http://localhost:8001/health`
2. Check CORS configuration allows localhost:3000
3. Verify backend is running: `curl http://localhost:8000/health`

---

### Issue 4: Agent Doesn't Call Tools

**Symptoms:**
- Agent responds but doesn't execute actions
- No "actions performed" indicator

**Fix:**
1. Check OpenAI API key is valid
2. Verify API key has credit: https://platform.openai.com/usage
3. Check model supports function calling (gpt-4o-mini does)

---

### Issue 5: CORS Error in Browser Console

**Symptoms:**
- "Access-Control-Allow-Origin" error
- Cross-origin request blocked

**Fix:** Verify CORS middleware in `src/mcp_server/server.py`:
```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-vercel-domain.vercel.app",
]
```

---

### Issue 6: Database Connection Failed

**Symptoms:**
- "Database connection failed" error
- Tasks not persisting

**Fix:**
```bash
# Verify DATABASE_URL
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check if tables exist
psql $DATABASE_URL -c "\dt"
```

---

### Issue 7: Conversation History Not Loading

**Architecture Note:** Chat history is stored in OpenAI's Conversations API, NOT in PostgreSQL. The frontend stores only `conversation_id` references in localStorage.

**Symptoms:**
- Previous conversations not showing in sidebar
- Context lost between messages

**Fix:**
1. Check localStorage has conversation data:
```javascript
// In browser console
console.log(localStorage.getItem('taskflow_conversations'));
```
2. Verify conversation_id is being returned from backend:
```bash
# Test chat endpoint - should return conversation_id
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "hello"}'
```
3. Check OpenAI API key has valid credit for Conversations API
4. Clear localStorage and start fresh conversation if corrupted:
```javascript
localStorage.removeItem('taskflow_conversations');
```

**Data Storage Summary:**
| Data | Location |
|------|----------|
| Users, Tasks | PostgreSQL (Neon) |
| Chat History | OpenAI Conversations API |
| Conversation IDs | Browser localStorage |

---

## Part 7: Cost Monitoring

### OpenAI API Pricing (gpt-4o-mini)

| Type | Cost |
|------|------|
| Input tokens | $0.15 / 1M tokens |
| Output tokens | $0.60 / 1M tokens |
| Average message | ~100-200 tokens |

### Estimated Usage with $7 Credit

```
$7 credit ≈ 46,000 input tokens + 11,600 output tokens
         ≈ 5,000-10,000 typical chat messages
```

### Monitor Usage

1. Visit: https://platform.openai.com/usage
2. Check daily/monthly breakdown
3. Set usage limits to avoid overspend

### Cost Optimization Tips

1. Keep system prompts concise
2. Limit conversation history to 10 messages
3. Use `gpt-4o-mini` (cheapest capable model)
4. Cache frequent queries if possible

---

## Part 8: Production Deployment Checklist

### Backend (Railway)

Before deploying:

- [ ] Add all environment variables to Railway:
  ```
  DATABASE_URL=postgresql://...
  JWT_SECRET_KEY=...
  OPENAI_API_KEY=sk-proj-...
  MCP_SERVER_PORT=8001
  MCP_BACKEND_URL=https://your-railway-app.railway.app
  FRONTEND_URL=https://your-vercel-app.vercel.app
  BACKEND_URL=https://your-railway-app.railway.app
  ```

- [ ] Verify health endpoints:
  ```bash
  curl https://your-railway-app.railway.app/health
  curl https://your-railway-app.railway.app:8001/health  # if MCP separate
  ```

- [ ] All 8 MCP tools accessible
- [ ] Database migrations applied
- [ ] Logs showing in Railway dashboard

### Frontend (Vercel)

Before deploying:

- [ ] Add environment variables to Vercel:
  ```
  NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
  NEXT_PUBLIC_CHAT_ENABLED=true
  ```

- [ ] Build succeeds locally:
  ```bash
  cd frontend && npm run build
  ```

- [ ] `/chat` route included in build
- [ ] Mobile responsive verified
- [ ] OAuth callbacks updated for production URLs

### Post-Deployment Verification

1. [ ] Sign up/Sign in works
2. [ ] Create task via dashboard
3. [ ] Create task via chat
4. [ ] OAuth login works (Google/GitHub)
5. [ ] Tasks sync between dashboard and chat
6. [ ] Mobile chat UI works
7. [ ] No CORS errors in production

---

## Part 9: Quick Reference Commands

```bash
# Start all services (run in 3 terminals)
# Terminal 1:
uv run uvicorn src.interfaces.api:app --reload --port 8000

# Terminal 2:
uv run python -m src.mcp_server.server

# Terminal 3:
cd frontend && npm run dev

# Run tests
uv run pytest tests/ -v

# Check service health
curl http://localhost:8000/health
curl http://localhost:8001/health

# View logs
tail -f logs/backend.log
tail -f logs/mcp.log
```

---

## Summary

Phase III adds AI-powered task management via natural language chat:

| Component | Port | Purpose |
|-----------|------|---------|
| FastAPI Backend | 8000 | REST API, Auth, Database |
| MCP Server | 8001 | AI Agent, Tool Execution |
| Next.js Frontend | 3000 | Web UI, Chat Interface |

**Key Files:**
- `src/mcp_server/agent.py` - OpenAI agent with function calling + OpenAIConversationsSession
- `src/mcp_server/tools.py` - 8 MCP tools for task management
- `src/models/chat.py` - Chat API models (no database models)
- `frontend/app/chat/page.tsx` - Chat UI with localStorage for conversation_ids

**Architecture (Stateless Backend):**
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

**Testing verified:**
- NLP unit tests passing
- All 8 MCP tools functional
- Cross-phase task synchronization
- Mobile responsive design
- Stateless chat architecture with OpenAI Conversations API

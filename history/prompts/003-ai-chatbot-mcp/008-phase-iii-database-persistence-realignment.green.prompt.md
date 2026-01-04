---
id: 008
title: Phase III Database Persistence Realignment
stage: green
date: 2026-01-04
surface: agent
model: claude-opus-4-5-20251101
feature: 003-ai-chatbot-mcp
branch: main
user: ps_qasim
command: /sp.implement
labels: ["phase-iii", "database", "persistence", "compliance", "chat-history"]
links:
  spec: specs/003-ai-chatbot-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/models/chat.py
  - src/db.py
  - src/mcp_server/agent.py
  - src/interfaces/api.py
  - frontend/app/chat/page.tsx
  - specs/003-ai-chatbot-mcp/tasks.md
tests:
  - python3 -m py_compile src/models/chat.py
  - python3 -m py_compile src/db.py
  - python3 -m py_compile src/mcp_server/agent.py
  - python3 -m py_compile src/interfaces/api.py
---

## Prompt

You are operating as a Hackathon II–compliant MCP coding agent.

CRITICAL INSTRUCTION:
This task is NOT about personal architecture preferences.
You MUST implement Phase III EXACTLY as defined in the official spec.

Before doing anything:
1. Read the file at root: @Hackathon II - Todo Spec-Driven Development.md
2. Focus ONLY on Phase III.
3. Follow the spec literally, not approximately.

MANDATORY TECHNOLOGIES (NO EXCEPTIONS):
- Frontend: OpenAI ChatKit
- Backend: FastAPI (Python)
- AI Framework: OpenAI Agents SDK (Agent + Runner)
- MCP Server: Official MCP SDK
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Auth: Better Auth

CORE REQUIREMENT (THIS IS THE FIX):
Re-align Phase III to use:
- Database-persisted chat history
- Stateless backend
- Agent SDK for reasoning
- MCP tools for task operations

## Response snapshot

### Implementation Summary

Re-aligned Phase III to be fully spec-compliant with database-persisted chat history:

1. **Added SQLModel Database Tables** (`src/models/chat.py`):
   - `ConversationDB`: Stores conversation metadata (user_id, title, timestamps)
   - `MessageDB`: Stores individual messages (conversation_id, role, content, tool_calls)

2. **Updated Database Initialization** (`src/db.py`):
   - Added ConversationDB and MessageDB to `create_tables()` function

3. **Refactored Agent** (`src/mcp_server/agent.py`):
   - Removed OpenAIConversationsSession dependency
   - Added database helper functions: `get_or_create_conversation`, `get_conversation_history`, `save_message`
   - Agent now loads history from PostgreSQL before processing
   - Messages are saved to database after each exchange

4. **Updated API Endpoints** (`src/interfaces/api.py`):
   - `POST /api/chat` and `POST /api/users/{user_id}/chat`: Database-backed chat
   - `GET /api/conversations` and `GET /api/users/{user_id}/conversations`: List conversations from DB
   - `GET /api/users/{user_id}/conversations/{id}`: Get conversation with messages
   - `GET /api/users/{user_id}/conversations/{id}/messages`: Paginated messages
   - `DELETE /api/conversations/{id}`: Delete from database

5. **Updated Frontend** (`frontend/app/chat/page.tsx`):
   - Replaced localStorage storage with API calls
   - `loadConversations()`: Fetches from database API
   - `selectConversation()`: Loads messages from database
   - `handleDeleteConversation()`: Deletes via API

### Key Compliance Points
- Server is stateless - all state comes from PostgreSQL
- Conversations persist across server restarts
- Messages stored in database, not OpenAI Conversations API
- Frontend sidebar shows database-backed conversations

## Outcome

- ✅ Impact: Phase III now stores chat history in PostgreSQL as required by spec
- 🧪 Tests: All Python files pass syntax check (py_compile)
- 📁 Files: 5 files modified, database models added, API endpoints updated, frontend refactored
- 🔁 Next prompts: Integration testing, E2E testing, deployment verification
- 🧠 Reflection: The original implementation relied on OpenAI's Conversations API for memory which violated the spec requirement for database persistence. This refactor ensures conversations persist across server restarts.

## Evaluation notes (flywheel)

- Failure modes observed: Previous implementation used OpenAI thread memory instead of PostgreSQL
- Graders run and results (PASS/FAIL): Syntax checks PASS, manual testing pending
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Run integration tests to verify conversation resume after server restart

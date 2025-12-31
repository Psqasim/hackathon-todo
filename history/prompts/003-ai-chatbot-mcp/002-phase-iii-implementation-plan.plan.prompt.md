---
id: 002
title: Phase III Implementation Plan
stage: plan
date: 2025-12-30
surface: agent
model: claude-opus-4-5-20251101
feature: 003-ai-chatbot-mcp
branch: 003-ai-chatbot-mcp
user: psqasim
command: /sp.plan
labels: ["phase-iii", "ai-chatbot", "mcp", "openai", "implementation-plan", "architecture"]
links:
  spec: specs/003-ai-chatbot-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-ai-chatbot-mcp/plan.md
  - specs/003-ai-chatbot-mcp/research.md
  - specs/003-ai-chatbot-mcp/data-model.md
  - specs/003-ai-chatbot-mcp/quickstart.md
  - specs/003-ai-chatbot-mcp/contracts/mcp-tools.yaml
  - specs/003-ai-chatbot-mcp/contracts/chat-api.yaml
tests:
  - Constitution check validation (PASS)
---

## Prompt

Reference @specs/003-ai-chatbot-mcp/spec.md and @.specify/memory/constitution.md

Create a detailed technical implementation plan for Phase III: AI Chatbot with MCP Integration.

## Technology Stack:

### MCP Server (New):
- **Framework:** FastMCP (Python MCP server library)
- **Language:** Python 3.12+
- **Port:** 8001
- **Protocol:** MCP (Model Context Protocol)
- **Dependencies:** fastmcp, httpx, pydantic

### OpenAI Integration:
- **SDK:** OpenAI Python SDK v1.0+
- **Model:** gpt-4o-mini
- **Features:** Function calling, streaming responses

### Frontend (Add to Existing):
- **New Route:** frontend/app/chat/page.tsx
- **Framework:** Next.js 16 (existing)
- **Styling:** Tailwind CSS (existing)
- **State:** React hooks

### Backend (No Changes):
- Existing FastAPI on port 8000
- Same JWT authentication
- Same agents

## Implementation Phases:
- Phase A: MCP Server Foundation
- Phase B: OpenAI Agent Integration
- Phase C: Chat API Endpoints
- Phase D: Frontend Chat UI
- Phase E: Database Persistence
- Phase F: Polish & Deployment

## Response snapshot

### Created Files:

| File | Description |
|------|-------------|
| `specs/003-ai-chatbot-mcp/plan.md` | Comprehensive implementation plan |
| `specs/003-ai-chatbot-mcp/research.md` | Technology research findings |
| `specs/003-ai-chatbot-mcp/data-model.md` | Database schema for Conversation/Message |
| `specs/003-ai-chatbot-mcp/quickstart.md` | Development setup guide |
| `specs/003-ai-chatbot-mcp/contracts/mcp-tools.yaml` | 8 MCP tool definitions |
| `specs/003-ai-chatbot-mcp/contracts/chat-api.yaml` | Chat REST API (OpenAPI 3.0) |

### Key Architecture Decisions:

1. **MCP Server as Middleware**: FastMCP server (port 8001) sits between frontend and FastAPI backend, handling OpenAI integration

2. **No Backend Changes**: All task operations use existing REST API endpoints via HTTP client

3. **SSE Streaming**: Server-Sent Events for real-time chat response streaming

4. **dateparser for NLP**: Natural language date parsing ("tomorrow", "next week")

5. **In-Memory + DB**: Conversation memory in-memory for session, persisted to PostgreSQL

### Constitution Compliance:

All 8 constitution principles validated:
- Agent Architecture Patterns ✅
- Skill Reusability Standards ✅
- Separation of Concerns ✅
- Evolution Strategy ✅
- Testing Standards ✅ (pending implementation)
- Code Quality ✅
- Error Handling ✅
- Spec-Driven Development ✅

### Implementation Phases:

| Phase | Components | Goal |
|-------|------------|------|
| A | 6 components | MCP Server Foundation |
| B | 6 components | OpenAI Agent Integration |
| C | 4 components | Chat API Endpoints |
| D | 7 components | Frontend Chat UI |
| E | 4 components | Database Persistence |
| F | 6 components | Polish & Deployment |

**Total**: 33 components across 6 phases

## Outcome

- Impact: Complete technical plan ready for `/sp.tasks` task generation
- Tests: Constitution check passed all gates
- Files: 6 planning artifacts created
- Next prompts: `/sp.tasks` to generate implementation tasks
- Reflection: Comprehensive plan with code examples, risk analysis, and success metrics

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - all constitution gates validated
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate FastMCP decorator syntax against latest library version

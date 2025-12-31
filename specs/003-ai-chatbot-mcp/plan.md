# Implementation Plan: AI Chatbot with MCP Integration

**Branch**: `003-ai-chatbot-mcp` | **Date**: 2025-12-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-ai-chatbot-mcp/spec.md`

---

## Summary

Phase III extends TaskFlow with an AI-powered conversational interface. Users can manage tasks through natural language commands in a chat interface. The implementation adds:

1. **MCP Server** (port 8001): Exposes 8 task management tools via FastMCP
2. **OpenAI Agent**: gpt-4o-mini with function calling for natural language understanding
3. **Chat UI**: New `/chat` route in existing Next.js frontend with streaming responses
4. **Conversation Persistence**: New database tables for chat history

The existing Phase II backend (FastAPI on port 8000) and database remain unchanged.

---

## Technical Context

**Language/Version**: Python 3.12+, TypeScript 5.x
**Primary Dependencies**:
- Backend: FastMCP 2.0, OpenAI SDK 1.0+, dateparser, httpx
- Frontend: Next.js 16, React 19, Tailwind CSS 4

**Storage**: Neon PostgreSQL (existing) + new Conversation/Message tables
**Testing**: pytest (backend), Jest (frontend)
**Target Platform**: Web (desktop + mobile), Linux server
**Project Type**: Web application (backend + frontend)
**Performance Goals**: <3s chat response, <30s task operations
**Constraints**: gpt-4o-mini model only, 10-message context window
**Scale/Scope**: Same user base as Phase II, ~100 concurrent chat sessions

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

### Agent Architecture Patterns ✅

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Multi-agent hierarchy | ✅ PASS | MCP Server as new agent, delegates to existing TaskManager via REST |
| Single responsibility | ✅ PASS | MCP tools handle I/O, OpenAI agent handles NLP, backend handles business logic |
| Typed message protocols | ✅ PASS | Pydantic models for all MCP tool inputs/outputs |
| No shared mutable state | ✅ PASS | MCP server stateless, conversation in DB |

### Skill Reusability Standards ✅

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Technology agnostic | ✅ PASS | MCP tools are interface-agnostic (no UI code) |
| Documented contracts | ✅ PASS | See contracts/mcp-tools.yaml |
| Stateless skills | ✅ PASS | State in PostgreSQL, not in tools |
| 90% test coverage | ⏳ PENDING | To be validated during implementation |

### Separation of Concerns ✅

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| UI layer separate | ✅ PASS | Chat UI (Next.js) → MCP Server → FastAPI |
| Business logic isolated | ✅ PASS | All task logic in existing TaskManagerAgent |
| Storage abstraction | ✅ PASS | MCP calls REST API, not database directly |

### Evolution Strategy ✅

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Builds on Phase II | ✅ PASS | No changes to existing endpoints or agents |
| Existing agents unchanged | ✅ PASS | TaskManagerAgent, StorageHandlerAgent untouched |
| New agent added | ✅ PASS | MCP Server as new communication layer |
| All tests pass | ⏳ PENDING | Phase II tests must pass with Phase III |

### Testing Standards ✅

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| TDD workflow | ✅ PASS | Tests first for MCP tools and chat UI |
| 80% coverage | ⏳ PENDING | Target during implementation |
| Unit/Integration/E2E | ✅ PASS | See test plan in components |

### Code Quality ✅

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Type hints | ✅ PASS | All functions typed |
| No Any types | ✅ PASS | Strict typing throughout |
| Docstrings | ✅ PASS | All public APIs documented |
| Max 50 lines/function | ✅ PASS | Small, focused functions |

### Error Handling ✅

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Graceful errors | ✅ PASS | User-friendly messages for all error types |
| Structured logging | ✅ PASS | structlog with JSON format |
| Correlation IDs | ✅ PASS | Request IDs for tracing |

### Spec-Driven Development ✅

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Specification first | ✅ PASS | spec.md created before plan |
| Agent contracts | ✅ PASS | contracts/mcp-tools.yaml, contracts/chat-api.yaml |
| Code references spec | ✅ PASS | Comments reference FR-XXX requirements |

---

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-chatbot-mcp/
├── spec.md              # Feature specification
├── plan.md              # This implementation plan
├── research.md          # Technology research findings
├── data-model.md        # Database schema additions
├── quickstart.md        # Development setup guide
├── contracts/           # API contracts
│   ├── mcp-tools.yaml   # MCP tool definitions
│   └── chat-api.yaml    # Chat REST API (OpenAPI)
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
src/
├── agents/              # Existing agents (unchanged)
├── backends/            # Existing storage (unchanged)
├── interfaces/
│   └── api.py           # Existing FastAPI (unchanged)
├── models/              # Existing + new models
│   ├── tasks.py         # Existing
│   ├── user.py          # Existing
│   └── chat.py          # NEW: Conversation, Message, ChatRequest
└── mcp_server/          # NEW: MCP Server package
    ├── __init__.py
    ├── server.py        # FastMCP server entry point
    ├── tools.py         # 8 MCP tool definitions
    ├── agent.py         # OpenAI agent configuration
    ├── backend_client.py # HTTP client for FastAPI
    ├── auth.py          # JWT validation
    ├── nlp.py           # Date/priority parsing
    ├── memory.py        # Conversation history
    └── prompts.py       # System prompts

frontend/
├── app/
│   └── chat/
│       └── page.tsx     # NEW: Chat page (Server Component)
├── components/
│   ├── chat-interface.tsx   # NEW: Main chat (Client Component)
│   └── chat/                # NEW: Chat subcomponents
│       ├── message-bubble.tsx
│       ├── chat-input.tsx
│       └── suggested-prompts.tsx
└── lib/
    └── chat-api.ts      # NEW: Chat API client

tests/
├── unit/
│   └── test_mcp_tools.py    # NEW: Tool unit tests
├── integration/
│   └── test_mcp_server.py   # NEW: Server integration tests
└── e2e/
    └── test_chat_flow.py    # NEW: End-to-end chat tests
```

**Structure Decision**: Web application structure with MCP server as additional backend service. Frontend adds new `/chat` route. No changes to existing Phase II structure.

---

## Implementation Phases

### Phase A: MCP Server Foundation

**Goal**: Create MCP server with tool definitions that call FastAPI backend

| Component | File | Description |
|-----------|------|-------------|
| A1 | `src/mcp_server/__init__.py` | Package initialization |
| A2 | `src/mcp_server/server.py` | FastMCP server with SSE transport |
| A3 | `src/mcp_server/backend_client.py` | HTTP client for FastAPI |
| A4 | `src/mcp_server/auth.py` | JWT token validation |
| A5 | `src/mcp_server/tools.py` | 8 MCP tool implementations |
| A6 | `tests/unit/test_mcp_tools.py` | Tool unit tests |

**Dependencies**: Phase II backend running
**Acceptance**: All 8 tools callable, return correct data

---

### Phase B: OpenAI Agent Integration

**Goal**: Connect OpenAI gpt-4o-mini to MCP tools with function calling

| Component | File | Description |
|-----------|------|-------------|
| B1 | `src/mcp_server/agent.py` | OpenAI client with function calling |
| B2 | `src/mcp_server/prompts.py` | System prompt for task assistant |
| B3 | `src/mcp_server/nlp.py` | Date and priority parsing |
| B4 | `src/mcp_server/memory.py` | Conversation history management |
| B5 | `src/models/chat.py` | Pydantic models for chat |
| B6 | `tests/unit/test_nlp.py` | NLP parsing tests |

**Dependencies**: Phase A complete
**Acceptance**: Agent understands "Add task X tomorrow" and calls correct tool

---

### Phase C: Chat API Endpoints

**Goal**: REST endpoints for chat interface to communicate with agent

| Component | File | Description |
|-----------|------|-------------|
| C1 | `src/mcp_server/server.py` | Add /api/chat POST endpoint |
| C2 | `src/mcp_server/server.py` | Add /api/conversations endpoints |
| C3 | `src/mcp_server/server.py` | SSE streaming response handler |
| C4 | `tests/integration/test_chat_api.py` | API integration tests |

**Dependencies**: Phase B complete
**Acceptance**: POST /api/chat returns streaming response

---

### Phase D: Frontend Chat UI

**Goal**: Beautiful, mobile-responsive chat interface

| Component | File | Description |
|-----------|------|-------------|
| D1 | `frontend/app/chat/page.tsx` | Chat page with auth check |
| D2 | `frontend/components/chat-interface.tsx` | Main chat component |
| D3 | `frontend/components/chat/message-bubble.tsx` | User/agent bubbles |
| D4 | `frontend/components/chat/chat-input.tsx` | Input with send button |
| D5 | `frontend/components/chat/suggested-prompts.tsx` | Quick action buttons |
| D6 | `frontend/lib/chat-api.ts` | Chat API client with SSE |
| D7 | `frontend/__tests__/chat.test.tsx` | Component tests |

**Dependencies**: Phase C complete
**Acceptance**: User can chat at /chat, messages stream in real-time

---

### Phase E: Database Persistence

**Goal**: Store conversation history in PostgreSQL

| Component | File | Description |
|-----------|------|-------------|
| E1 | `src/models/chat.py` | ConversationDB, MessageDB models |
| E2 | `src/db.py` | Add conversation tables to create_tables |
| E3 | `src/mcp_server/memory.py` | Database persistence layer |
| E4 | `tests/integration/test_chat_persistence.py` | Persistence tests |

**Dependencies**: Phase D complete
**Acceptance**: Conversations persist across page refresh

---

### Phase F: Polish & Deployment

**Goal**: Mobile optimization, error handling, deployment

| Component | File | Description |
|-----------|------|-------------|
| F1 | Frontend CSS | Mobile-first responsive design |
| F2 | Error handling | User-friendly error messages |
| F3 | `Procfile` | Add MCP server to Railway |
| F4 | `.env.example` | Add OpenAI configuration |
| F5 | `README.md` | Update with Phase III instructions |
| F6 | `tests/e2e/test_chat_flow.py` | End-to-end tests |

**Dependencies**: Phase E complete
**Acceptance**: Chat works on mobile, deployed to Railway + Vercel

---

## Component Specifications

### A2: FastMCP Server (src/mcp_server/server.py)

```python
from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

mcp = FastMCP(
    name="TaskFlow MCP Server",
    description="AI-powered task management via natural language"
)

# Add CORS for frontend
mcp.app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://hackathon-todo-orcin.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(mcp.app, host="0.0.0.0", port=8001)
```

### A5: MCP Tools (src/mcp_server/tools.py)

```python
from fastmcp import tool

@mcp.tool
async def add_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: str | None = None,
    tags: list[str] | None = None
) -> dict:
    """Create a new task for the authenticated user.

    Args:
        title: Task title (required)
        description: Optional task description
        priority: low, medium, high, or urgent
        due_date: Due date in YYYY-MM-DD format
        tags: List of tags for categorization

    Returns:
        Created task with ID
    """
    # Call FastAPI backend
    response = await backend_client.post(
        f"/api/users/{user_id}/tasks",
        json={
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "tags": tags or []
        }
    )
    return {"success": True, "task": response.json()["task"]}
```

### B1: OpenAI Agent (src/mcp_server/agent.py)

```python
from openai import OpenAI

class TaskAgent:
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-4o-mini"
        self.temperature = 0.7
        self.tools = self._build_tools()

    async def chat(
        self,
        message: str,
        conversation_history: list[dict],
        user_id: str
    ) -> AsyncIterator[str]:
        """Process user message and stream response."""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *conversation_history,
            {"role": "user", "content": message}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            stream=True
        )

        async for chunk in response:
            # Handle streaming response and tool calls
            yield chunk
```

### D2: Chat Interface (frontend/components/chat-interface.tsx)

```typescript
'use client';

import { useState, useEffect, useRef } from 'react';
import { MessageBubble } from './chat/message-bubble';
import { ChatInput } from './chat/chat-input';
import { SuggestedPrompts } from './chat/suggested-prompts';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const handleSend = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    // Stream response from MCP server
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: content })
    });

    // Handle SSE streaming
    const reader = response.body?.getReader();
    // ... stream handling
  };

  return (
    <div className="flex flex-col h-screen">
      <header className="border-b p-4">
        <h1 className="text-xl font-semibold">TaskFlow Chat</h1>
      </header>

      <main className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 && <SuggestedPrompts onSelect={handleSend} />}
        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </main>

      <ChatInput onSend={handleSend} disabled={loading} />
    </div>
  );
}
```

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OpenAI rate limiting | Medium | Medium | Implement retry with backoff |
| High API costs | Low | Medium | Use gpt-4o-mini, limit context |
| MCP server latency | Low | High | Connection pooling, caching |
| Mobile UX issues | Medium | Medium | Test on actual devices |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Chat response time | <3 seconds | Performance monitoring |
| Task operation accuracy | >90% | Manual testing |
| Mobile usability | 320px+ | Responsive testing |
| Test coverage | >80% | pytest --cov |
| User stories complete | 7/7 | Acceptance testing |

---

## Next Steps

1. Run `/sp.tasks` to generate implementation tasks
2. Set up OpenAI API key in development environment
3. Begin Phase A: MCP Server Foundation
4. Create feature branch for first component

---

## Complexity Tracking

No constitution violations requiring justification. All complexity is necessary for the feature requirements.

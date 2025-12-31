# Research: AI Chatbot with MCP Integration

**Feature**: 003-ai-chatbot-mcp
**Date**: 2025-12-30
**Status**: Complete

---

## Research Questions & Decisions

### 1. MCP Server Framework Selection

**Question**: Which MCP server framework should we use for Python?

**Decision**: FastMCP 2.0

**Rationale**:
- FastMCP is the production-ready framework for MCP server development
- FastMCP 1.0 was incorporated into the official MCP SDK
- Simple decorator-based API (`@mcp.tool`) aligns with our FastAPI patterns
- Automatic JSON schema generation from type hints
- Built-in support for STDIO and SSE transports
- Active maintenance and comprehensive documentation

**Alternatives Considered**:
| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| Official MCP SDK | Official support | Lower-level API | More boilerplate |
| Custom implementation | Full control | Significant effort | Time-to-market |

**Sources**:
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [FastMCP Documentation](https://gofastmcp.com/tutorials/create-mcp-server)

---

### 2. OpenAI SDK Function Calling Pattern

**Question**: How to implement function calling with streaming for gpt-4o-mini?

**Decision**: Use OpenAI Python SDK v1.0+ with Chat Completions API and `tools` parameter

**Rationale**:
- Native function calling support in Chat Completions API
- Structured outputs with strict mode for reliable tool calls
- Streaming support via `stream=True` parameter
- gpt-4o-mini supports function calling with lower cost than gpt-4o

**Implementation Pattern**:
```python
from openai import OpenAI

client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                    "due_date": {"type": "string", "format": "date"}
                },
                "required": ["title"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    stream=True
)
```

**Sources**:
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI Streaming Guide](https://platform.openai.com/docs/guides/streaming-responses)

---

### 3. Natural Language Date Parsing

**Question**: How to parse natural language dates like "tomorrow", "next week"?

**Decision**: Use dateparser library

**Rationale**:
- Python library specifically designed for natural language date parsing
- Supports relative dates: "tomorrow", "in 3 days", "next week"
- Supports multiple languages (auto-detection)
- Active maintenance, well-documented
- Simple API: `dateparser.parse("tomorrow")`

**Implementation Pattern**:
```python
import dateparser
from datetime import datetime

def parse_natural_date(text: str) -> datetime | None:
    """Parse natural language date expressions."""
    return dateparser.parse(
        text,
        settings={
            'PREFER_DATES_FROM': 'future',
            'RELATIVE_BASE': datetime.now()
        }
    )

# Examples:
# "tomorrow" → 2025-12-31 00:00:00
# "next week" → 2026-01-06 00:00:00
# "in 3 days" → 2026-01-02 00:00:00
```

**Sources**:
- [dateparser PyPI](https://pypi.org/project/dateparser/)
- [dateparser Documentation](https://dateparser.readthedocs.io/en/latest/)

---

### 4. Chat API Architecture

**Question**: How should the chat endpoint communicate with the MCP server and OpenAI?

**Decision**: Single chat endpoint on MCP server that handles OpenAI communication

**Rationale**:
- MCP server is the natural integration point
- Keeps OpenAI API key on backend only (security)
- MCP tools are locally available to the chat handler
- Simplifies frontend - just sends messages to one endpoint

**Architecture**:
```
Frontend (/chat) → MCP Server (port 8001) → OpenAI API
                        ↓
                   MCP Tools → FastAPI Backend (port 8000)
```

**Endpoint Design**:
```
POST /api/chat
Headers: Authorization: Bearer <jwt_token>
Body: { "message": "Add task to buy groceries tomorrow" }
Response: SSE stream of agent responses
```

---

### 5. Conversation Memory Strategy

**Question**: How to maintain conversation context?

**Decision**: In-memory conversation storage with database persistence

**Rationale**:
- Phase III: In-memory for simplicity (user-keyed dict)
- Future: Database persistence for cross-session continuity
- Limit to 10 messages per user (context window management)
- Store both user messages and assistant responses

**Implementation**:
```python
from collections import defaultdict

# In-memory storage: user_id -> list of messages
conversations: dict[str, list[dict]] = defaultdict(list)

def add_message(user_id: str, role: str, content: str) -> None:
    conversations[user_id].append({"role": role, "content": content})
    # Keep only last 10 messages
    if len(conversations[user_id]) > 10:
        conversations[user_id] = conversations[user_id][-10:]
```

---

### 6. Frontend Chat Integration

**Question**: How to integrate chat UI with existing Next.js app?

**Decision**: New `/chat` route with Client Component for real-time chat

**Rationale**:
- Follows existing app structure (app router)
- Client Component required for real-time state (useState, useEffect)
- SSE for streaming responses (better UX than polling)
- Reuse existing auth context and API client patterns

**Implementation**:
```typescript
// frontend/app/chat/page.tsx (Server Component wrapper)
export default function ChatPage() {
  // Auth check happens here
  return <ChatInterface />;
}

// frontend/components/chat-interface.tsx (Client Component)
'use client';
export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  // Handle SSE streaming, message submission, etc.
}
```

---

### 7. Authentication Flow

**Question**: How does JWT flow through the chat system?

**Decision**: Pass JWT from frontend → MCP server → FastAPI backend

**Rationale**:
- Reuse existing Phase II JWT authentication
- MCP server validates token and extracts user_id
- MCP server adds token to all backend API calls
- User isolation maintained at all layers

**Flow**:
```
1. User logged in (has JWT token in localStorage)
2. Frontend sends message + JWT to MCP server
3. MCP server decodes JWT to get user_id
4. MCP tools call FastAPI with JWT in Authorization header
5. FastAPI validates JWT and returns user-scoped data
```

---

### 8. Error Handling Strategy

**Question**: How to handle various error scenarios gracefully?

**Decision**: Layered error handling with user-friendly messages

| Error Type | Detection | User Message |
|------------|-----------|--------------|
| OpenAI rate limit | 429 status | "I'm a bit busy. Please try again in a moment." |
| MCP server down | Connection refused | "Chat service is temporarily unavailable." |
| Backend error | 500 status | "Something went wrong. Please try again." |
| Auth expired | 401 status | Redirect to /signin |
| Network offline | fetch error | "You appear to be offline. Check your connection." |

---

## Dependencies to Add

### Backend (pyproject.toml)

```toml
[project.dependencies]
fastmcp = ">=2.0.0"
openai = ">=1.0.0"
dateparser = ">=1.2.0"
httpx = ">=0.27.0"  # Already present from Phase II
```

### Frontend (package.json)

No new dependencies required. Using:
- fetch API for HTTP requests
- EventSource for SSE (built-in)
- Existing Tailwind CSS for styling

---

## Open Questions Resolved

1. **MCP transport protocol?** → SSE for web (STDIO for local/Claude Desktop)
2. **OpenAI model?** → gpt-4o-mini (cost-effective, supports function calling)
3. **Date parsing library?** → dateparser (Python)
4. **Conversation storage?** → In-memory Phase III, PostgreSQL future
5. **Frontend streaming?** → Server-Sent Events (SSE)

---

## Next Steps

1. Create data-model.md with Conversation/Message entities
2. Define API contracts in contracts/
3. Create quickstart.md with development setup
4. Update plan.md with technical context

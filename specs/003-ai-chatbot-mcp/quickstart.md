# Quickstart: AI Chatbot with MCP Integration

**Feature**: 003-ai-chatbot-mcp
**Date**: 2025-12-30

---

## Prerequisites

Before starting Phase III development, ensure you have:

1. **Phase II Running**:
   - FastAPI backend on port 8000
   - Next.js frontend on port 3000
   - PostgreSQL database (Neon) configured

2. **OpenAI API Key**:
   - Sign up at [OpenAI Platform](https://platform.openai.com/)
   - Create an API key with access to gpt-4o-mini
   - Have at least $5 credit (gpt-4o-mini is cost-effective)

3. **Python Environment**:
   - Python 3.12+ installed
   - UV package manager configured

---

## Quick Setup

### 1. Install New Dependencies

```bash
# From repository root
uv add fastmcp openai dateparser
```

### 2. Configure Environment

Add to your `.env` file:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here

# MCP Server Configuration
MCP_SERVER_PORT=8001
MCP_BACKEND_URL=http://localhost:8000
```

### 3. Create MCP Server Structure

```bash
mkdir -p src/mcp_server
touch src/mcp_server/__init__.py
touch src/mcp_server/server.py
touch src/mcp_server/tools.py
touch src/mcp_server/agent.py
touch src/mcp_server/nlp.py
```

### 4. Start MCP Server

```bash
# Run MCP server (port 8001)
uv run python -m src.mcp_server.server
```

### 5. Start All Services

Terminal 1 - FastAPI Backend:
```bash
uv run uvicorn src.interfaces.api:app --reload --port 8000
```

Terminal 2 - MCP Server:
```bash
uv run python -m src.mcp_server.server
```

Terminal 3 - Next.js Frontend:
```bash
cd frontend && npm run dev
```

---

## Verification Steps

### 1. Verify MCP Server Health

```bash
curl http://localhost:8001/health
# Expected: {"status": "healthy", "openai_configured": true, "backend_reachable": true}
```

### 2. Test Chat Endpoint

```bash
# Get a JWT token first (sign in via Phase II)
TOKEN="your-jwt-token"

# Send a test message
curl -X POST http://localhost:8001/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my tasks"}'
```

### 3. Open Chat UI

Navigate to: http://localhost:3000/chat

---

## Development Workflow

### MCP Tool Development

1. Define tool in `src/mcp_server/tools.py`:
   ```python
   @mcp.tool
   def add_task(title: str, description: str = "", priority: str = "medium") -> dict:
       """Create a new task for the user."""
       # Implementation here
       return {"success": True, "task": {...}}
   ```

2. Test tool in isolation:
   ```bash
   uv run pytest tests/unit/test_mcp_tools.py -k test_add_task
   ```

3. Test with agent:
   ```bash
   curl -X POST http://localhost:8001/api/chat \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"message": "Add task to test MCP tools"}'
   ```

### Frontend Chat Development

1. Start frontend with hot reload:
   ```bash
   cd frontend && npm run dev
   ```

2. Open http://localhost:3000/chat

3. Edit `frontend/components/chat-interface.tsx`

4. Changes reflect immediately

---

## Troubleshooting

### OpenAI Rate Limiting

If you see "429 Too Many Requests":
- Wait 60 seconds and retry
- Check your OpenAI usage dashboard
- Consider using exponential backoff

### MCP Server Connection Issues

If chat UI can't connect:
```bash
# Check if MCP server is running
curl http://localhost:8001/health

# Check logs
tail -f mcp_server.log
```

### JWT Token Issues

If you see "401 Unauthorized":
1. Ensure you're logged in to Phase II web app
2. Check token in localStorage: `localStorage.getItem('token')`
3. Verify token hasn't expired

### Backend Connection Issues

If MCP server can't reach FastAPI:
```bash
# Test backend directly
curl http://localhost:8000/health

# Check MCP server config
echo $MCP_BACKEND_URL
```

---

## File Structure Overview

```
src/mcp_server/
├── __init__.py          # Package init
├── server.py            # FastMCP server entry point
├── tools.py             # MCP tool definitions
├── agent.py             # OpenAI agent configuration
├── backend_client.py    # HTTP client for FastAPI
├── auth.py              # JWT validation
├── nlp.py               # Date/priority parsing
├── memory.py            # Conversation history
└── prompts.py           # System prompts

frontend/
├── app/
│   └── chat/
│       └── page.tsx     # Chat page (Server Component)
├── components/
│   ├── chat-interface.tsx   # Main chat (Client Component)
│   └── chat/
│       ├── message-bubble.tsx
│       ├── chat-input.tsx
│       └── suggested-prompts.tsx
└── lib/
    └── chat-api.ts      # Chat API client
```

---

## Environment Variables Reference

### Backend (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `MCP_SERVER_PORT` | MCP server port | 8001 |
| `MCP_BACKEND_URL` | FastAPI backend URL | http://localhost:8000 |

### Frontend (.env.local)

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | FastAPI backend URL | http://localhost:8000 |
| `NEXT_PUBLIC_MCP_URL` | MCP server URL | http://localhost:8001 |

---

## Next Steps

1. Read [spec.md](./spec.md) for detailed requirements
2. Read [research.md](./research.md) for technology decisions
3. Read [data-model.md](./data-model.md) for database schema
4. Check [contracts/](./contracts/) for API specifications
5. Run `/sp.tasks` to generate implementation tasks

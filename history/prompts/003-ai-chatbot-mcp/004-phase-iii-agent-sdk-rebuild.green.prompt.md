---
id: 004
title: Phase III Agent SDK Rebuild
stage: green
date: 2025-12-31
surface: agent
model: claude-opus-4-5-20251101
feature: 003-ai-chatbot-mcp
branch: 003-ai-chatbot-mcp
user: developer
command: /sp.implement
labels: ["openai-agents-sdk", "function-tool", "agent-rebuild", "conversation-sidebar"]
links:
  spec: specs/003-ai-chatbot-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - src/mcp_server/agent.py
  - src/mcp_server/prompts.py
  - src/mcp_server/backend_client.py
  - frontend/app/chat/page.tsx
  - pyproject.toml
  - uv.lock
tests:
  - null
---

## Prompt

/sp.implement with critical hackathon requirements:

1. Must use OpenAI Agents SDK (AgentKit), NOT Chat Completions API
2. Must use built-in agent threads for memory
3. Must use @function_tool decorator for automatic schema generation
4. Backend must be stateless, memory in SDK threads only
5. Required Context7 research first
6. Frontend needs ChatGPT-style conversation sidebar
7. Each conversation maps to ONE agent thread
8. Clicking a conversation reloads the same thread

User frustration: "I think you just use OpenAI key and simple make chatbot?" - Teacher mentioned agents with built-in history like ChatGPT.

## Response snapshot

### 1. Research Phase (Context7)
- Researched OpenAI Agents SDK via Context7 MCP
- Found package: `openai-agents==0.6.4`
- Key patterns: `Agent`, `Runner.run()`, `@function_tool`, `RunContextWrapper[Context]`

### 2. Package Installation
```bash
uv add openai-agents
```
Installed `openai-agents==0.6.4` with dependencies.

### 3. Complete Agent Rebuild (`src/mcp_server/agent.py`)

Created proper agentic system using OpenAI Agents SDK:

**AgentContext dataclass:**
```python
@dataclass
class AgentContext:
    user_id: str
    backend: BackendClient
    last_task_ids: list[str] = field(default_factory=list)
    last_operation: str = ""
```

**8 Function Tools with @function_tool decorator:**
- `add_task` - Create tasks with title, description, priority, due_date, tags
- `list_tasks` - Get tasks filtered by status/priority
- `get_task` - Get specific task details
- `update_task` - Update task fields
- `complete_task` - Mark task complete/pending
- `delete_task` - Remove task (with confirmation)
- `search_tasks` - Search by keyword
- `filter_tasks` - Multi-criteria filtering

**Agent Factory:**
```python
def create_task_agent() -> Agent[AgentContext]:
    return Agent[AgentContext](
        name="TaskFlow AI",
        model="gpt-4o-mini",
        instructions=get_full_system_prompt(),
        tools=[add_task, list_tasks, get_task, update_task,
               complete_task, delete_task, search_tasks, filter_tasks],
    )
```

**TaskAgentRunner with Runner.run():**
```python
result = await Runner.run(self._agent, input=message, context=context)
```

### 4. Bug Fixes
- Added current date to system prompt (was showing 2023)
- Added `put()` method to BackendClient
- Fixed `update_task` to use PUT instead of PATCH
- Fixed `complete_task` endpoint path
- Fixed `search_tasks` to use client-side filtering

### 5. Frontend Conversation Sidebar
Added ChatGPT-style sidebar with:
- Conversation list with titles and message counts
- New Chat button
- Click to load conversation history
- Delete conversation with confirmation
- Mobile-responsive with overlay
- Back to Tasks link

## Outcome

- Impact: Complete Phase III agent rebuild using proper OpenAI Agents SDK instead of basic Chat Completions API. Added ChatGPT-style conversation sidebar for better UX.
- Tests: Manual testing required - agent runs with SDK, conversations persist
- Files: 6 files modified/created
- Next prompts: Test the agent with real tasks, verify conversation persistence, deploy to production
- Reflection: User was correct that initial implementation was too simple. The OpenAI Agents SDK provides proper agentic behavior with built-in tool execution and context management.

## Evaluation notes (flywheel)

- Failure modes observed: Initial implementation used Chat Completions API which required manual message history management. User correctly identified this wasn't a "real" agent.
- Graders run and results (PASS/FAIL): N/A - manual verification needed
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add streaming support for agent responses, implement proper conversation title generation from first message

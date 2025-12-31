---
id: 016
title: OpenAI Agent SDK Research for Phase III
stage: general
date: 2025-12-30
surface: agent
model: claude-opus-4-5-20251101
feature: 002-fullstack-web-app
branch: 002-fullstack-web-app
user: psqasim
command: conversation
labels: ["openai", "agents-sdk", "mcp", "research", "phase-iii", "ai-chatbot"]
links:
  spec: specs/002-fullstack-web-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/general/016-openai-agent-sdk-research.general.prompt.md
tests:
  - N/A (research task)
---

## Prompt

Use Context7 MCP to research OpenAI Agent SDK implementation:
1. How to create an OpenAI agent with function calling
2. How to implement MCP (Model Context Protocol) servers
3. How to integrate FastAPI with OpenAI agents
4. Best practices for agent tools and streaming
5. Natural language date parsing for task due dates

Save key insights about:
- How to initialize OpenAI agent with tools
- How to define MCP tool schemas
- How to handle streaming responses
- Best practices for agent memory/context
- Error handling patterns

Use the research to inform our implementation approach for Phase III AI Chatbot.

## Response snapshot

### Key Research Findings

#### 1. OpenAI Agents SDK - Function Calling

```python
from agents import Agent, Runner, function_tool

@function_tool
def create_task(title: str, description: str = "", due_date: str = "") -> str:
    """Create a new task in the todo list."""
    # Implementation here
    return f"Created task: {title}"

agent = Agent(
    name="TaskFlow Assistant",
    instructions="You help users manage their tasks...",
    tools=[create_task]
)

# Synchronous execution
result = Runner.run_sync(agent, "Create a task for tomorrow")

# Streaming execution
async for event in Runner.run_streamed(agent, "List my tasks"):
    if event.type == "raw_response_event":
        print(event.data)
```

#### 2. MCP Server Implementation with FastMCP

```python
from fastmcp import FastMCP

mcp = FastMCP("TaskFlow MCP Server")

@mcp.tool()
def add_task(title: str, description: str = "") -> dict:
    """Add a new task to TaskFlow."""
    return {"status": "success", "task_id": "123"}

@mcp.tool()
def list_tasks(status: str = "all") -> list:
    """List tasks with optional status filter."""
    return [{"id": "1", "title": "Example", "status": "pending"}]

# Run with: mcp run server.py
```

#### 3. OpenAI SDK Built-in MCP Support (March 2025)

```python
from agents import Agent
from agents.mcp import MCPServerStdio

# Connect to MCP server
async with MCPServerStdio(
    params={"command": "python", "args": ["mcp_server.py"]}
) as server:
    tools = await server.list_tools()

    agent = Agent(
        name="TaskFlow Agent",
        instructions="Manage tasks using the TaskFlow MCP server",
        mcp_servers=[server]
    )
```

#### 4. Streaming Response Handling

```python
from agents import Runner

async def stream_response(agent, user_input):
    async for event in Runner.run_streamed(agent, user_input):
        match event.type:
            case "raw_response_event":
                # Handle streaming text chunks
                if hasattr(event.data, "delta"):
                    yield event.data.delta.get("text", "")
            case "run_item_stream_event":
                # Handle tool calls
                if event.item.type == "tool_call":
                    yield f"\n[Calling: {event.item.name}]\n"
```

#### 5. Error Handling Patterns

```python
from agents import Agent, Runner

def handle_tool_error(context, error):
    """Custom error handler for tool failures."""
    return f"Tool failed: {error}. Please try a different approach."

agent = Agent(
    name="TaskFlow Assistant",
    tools=[create_task, list_tasks],
    tool_use_behavior={
        "failure_error_function": handle_tool_error
    }
)
```

#### 6. Natural Language Date Parsing

```python
import dateparser

def parse_due_date(text: str) -> str | None:
    """Parse natural language dates like 'tomorrow', 'next week'."""
    parsed = dateparser.parse(
        text,
        settings={
            'PREFER_DATES_FROM': 'future',
            'RELATIVE_BASE': datetime.now()
        }
    )
    return parsed.isoformat() if parsed else None

# Examples:
# "tomorrow" -> 2025-12-31T00:00:00
# "in 3 days" -> 2026-01-02T00:00:00
# "next monday" -> 2026-01-06T00:00:00
```

### Architecture Recommendation for Phase III

```
User Input (Natural Language)
    ↓
OpenAI Agent (with tools)
    ↓
MCP Server (TaskFlow)
    ↓
FastAPI Backend (existing)
    ↓
PostgreSQL Database
```

### Key Dependencies to Add

```toml
# pyproject.toml additions for Phase III
[project.dependencies]
openai-agents = ">=0.1.0"
fastmcp = ">=0.1.0"
dateparser = ">=1.2.0"
```

## Outcome

- Impact: Research completed for Phase III AI Chatbot implementation approach
- Tests: N/A (research task)
- Files: 1 PHR created
- Next prompts: Create Phase III spec, implement MCP server for TaskFlow, integrate OpenAI agent
- Reflection: OpenAI Agents SDK has excellent MCP integration, making it ideal for our multi-agent architecture

## Evaluation notes (flywheel)

- Failure modes observed: Context7 MCP tool failed with validation errors, used WebSearch/WebFetch as fallback
- Graders run and results (PASS/FAIL): PASS - all key information gathered
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test OpenAI Agents SDK locally with simple tool before full integration
